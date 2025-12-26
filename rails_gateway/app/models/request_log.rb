# RequestLog model - Persists all API requests for auditing
class RequestLog < ApplicationRecord
  validates :store_id, presence: true
  validates :question, presence: true

  # Scopes for filtering
  scope :recent, -> { order(created_at: :desc).limit(100) }
  scope :for_store, ->(store_id) { where(store_id: store_id) }
  scope :successful, -> { where(success: true) }
  scope :failed, -> { where(success: false) }

  def self.log_request(store_id:, question:, response: nil, success: true, error: nil)
    create!(
      store_id: store_id,
      question: question,
      response: response.to_json,
      success: success,
      error_message: error,
      response_time_ms: 0
    )
  end
end
