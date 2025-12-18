module Api
  module V1
    class QuestionsController < ApplicationController
      # POST /api/v1/questions
      def create
        store_id = params[:store_id]
        question = params[:question]

        # 1. Validation
        if store_id.blank? || question.blank?
          return render json: { error: "Missing required parameters: store_id, question" }, status: :unprocessable_entity
        end

        # 2. Authorization: Retrieve the token for this specific store
        shop = Shop.find_by(shopify_domain: store_id)
        if shop.nil? || shop.shopify_token.blank?
          return render json: { error: "Shop not authorized. Please install the app first." }, status: :unauthorized
        end

        # 3. Logging
        Rails.logger.info "Processing question for store #{store_id}: #{question}"

        # 4. Forward to Python AI Service (passing the token)
        response = PythonAiService.ask(store_id, question, shop.shopify_token)

        if response[:success]
          render json: response[:data]
        else
          render json: { error: "AI Service Error", details: response[:error] }, status: :bad_gateway
        end
      end
    end
  end
end
