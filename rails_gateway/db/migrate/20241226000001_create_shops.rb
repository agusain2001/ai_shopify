# Migration to create shops table for storing Shopify store tokens
class CreateShops < ActiveRecord::Migration[7.1]
  def change
    create_table :shops do |t|
      t.string :domain, null: false, index: { unique: true }
      t.string :access_token, null: false
      t.string :scope
      t.timestamps
    end
  end
end
