# Migration to create request_logs table for auditing API requests
class CreateRequestLogs < ActiveRecord::Migration[7.1]
  def change
    create_table :request_logs do |t|
      t.string :store_id, null: false, index: true
      t.text :question, null: false
      t.text :response
      t.boolean :success, default: true
      t.string :error_message
      t.integer :response_time_ms
      t.timestamps
    end

    add_index :request_logs, :created_at
  end
end
