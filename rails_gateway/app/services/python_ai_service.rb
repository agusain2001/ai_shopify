require 'httparty'

class PythonAiService
  include HTTParty
  # In Docker, 'python-ai-agent' is the hostname from docker-compose
  # In local dev, it might be 'http://localhost:8000'
  base_uri ENV.fetch('PYTHON_SERVICE_URL', 'http://python-ai-agent:8000')

  def self.ask(store_id, question, access_token)
    begin
      response = post('/analyze', 
        body: { 
          store_id: store_id, 
          question: question,
          access_token: access_token # <--- Pass the token here
        }.to_json,
        headers: { 'Content-Type' => 'application/json' }
      )

      if response.success?
        { success: true, data: JSON.parse(response.body) }
      else
        { success: false, error: response.body }
      end
    rescue Errno::ECONNREFUSED
      { success: false, error: "Python AI Service is invalid or offline." }
    rescue StandardError => e
      { success: false, error: e.message }
    end
  end
end
