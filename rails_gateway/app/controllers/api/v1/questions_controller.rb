module Api
  module V1
    class QuestionsController < ApplicationController
      # POST /api/v1/questions
      def create
        store_id = params[:store_id]
        question = params[:question]
        start_time = Time.now

        # 1. Validation
        if store_id.blank? || question.blank?
          return render json: { error: "Missing required parameters: store_id, question" }, status: :unprocessable_entity
        end

        # 2. Log Request Start
        Rails.logger.info "Processing question for store #{store_id}: #{question}"

        # 3. Forward to Python AI Service
        response = PythonAiService.ask(store_id, question)
        response_time_ms = ((Time.now - start_time) * 1000).to_i

        # 4. Persist Request Log to Database
        begin
          RequestLog.create!(
            store_id: store_id,
            question: question,
            response: response[:data].to_json,
            success: response[:success],
            error_message: response[:error],
            response_time_ms: response_time_ms
          )
        rescue => e
          Rails.logger.error "Failed to log request: #{e.message}"
        end

        # 5. Return Response
        if response[:success]
          render json: response[:data]
        else
          render json: { error: "AI Service Error", details: response[:error] }, status: :bad_gateway
        end
      end
    end
  end
end