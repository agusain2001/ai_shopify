# Database Schema for Shopify AI Analytics
# This file is auto-generated from migrations

ActiveRecord::Schema[7.1].define(version: 2024_12_26_000002) do
  create_table "shops", force: :cascade do |t|
    t.string "domain", null: false
    t.string "access_token", null: false
    t.string "scope"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["domain"], name: "index_shops_on_domain", unique: true
  end

  create_table "request_logs", force: :cascade do |t|
    t.string "store_id", null: false
    t.text "question", null: false
    t.text "response"
    t.boolean "success", default: true
    t.string "error_message"
    t.integer "response_time_ms"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["store_id"], name: "index_request_logs_on_store_id"
    t.index ["created_at"], name: "index_request_logs_on_created_at"
  end
end
