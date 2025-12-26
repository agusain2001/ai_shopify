# Shop model - Stores connected Shopify stores and their access tokens
class Shop < ApplicationRecord
  validates :domain, presence: true, uniqueness: true
  validates :access_token, presence: true

  # Encrypt the access token at rest (Rails 7+ built-in encryption)
  # In production, use: encrypts :access_token

  def self.find_by_domain(domain)
    find_by(domain: normalize_domain(domain))
  end

  def self.store_token(domain:, access_token:)
    shop = find_or_initialize_by(domain: normalize_domain(domain))
    shop.access_token = access_token
    shop.save!
    shop
  end

  private

  def self.normalize_domain(domain)
    domain.to_s.downcase.strip
  end
end
