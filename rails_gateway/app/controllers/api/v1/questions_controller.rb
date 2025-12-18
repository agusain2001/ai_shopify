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

        # 2. Log Request (Optional Persistence could go here)
        Rails.logger.info "Processing question for store #{store_id}: #{question}"

        # 3. Forward to Python AI Service
        response = PythonAiService.ask(store_id, question)

        if response[:success]
          render json: response[:data]
        else
          render json: { error: "AI Service Error", details: response[:error] }, status: :bad_gateway
        end
      end
    end
  end
end