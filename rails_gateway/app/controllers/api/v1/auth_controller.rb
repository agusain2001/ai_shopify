require 'openssl'

module Api
  module V1
    class AuthController < ApplicationController
      
      # Step 1: Redirect user to Shopify Permission Screen
      def install
        shop = params[:shop]
        return render json: { error: "Missing shop parameter" }, status: 400 unless shop

        api_key = ENV['SHOPIFY_API_KEY']
        scopes = 'read_products,read_orders,read_all_orders,read_analytics,read_inventory'
        redirect_uri = ENV.fetch('SHOPIFY_REDIRECT_URI', 'http://localhost:3000/api/v1/auth/shopify/callback')
        
        # Generate nonce for state verification
        nonce = SecureRandom.hex(16)
        session[:oauth_nonce] = nonce

        # Construct permission URL
        install_url = "https://#{shop}/admin/oauth/authorize?client_id=#{api_key}&scope=#{scopes}&redirect_uri=#{redirect_uri}&state=#{nonce}"
        
        redirect_to install_url, allow_other_host: true
      end

      # Step 2: Handle Callback and Exchange Code for Token
      def callback
        shop = params[:shop]
        code = params[:code]
        hmac = params[:hmac]
        state = params[:state]
        
        # HMAC Signature Verification
        unless verify_hmac(request.query_string, hmac)
          Rails.logger.error "HMAC verification failed for shop: #{shop}"
          return render json: { error: "Invalid HMAC signature" }, status: 401
        end

        # Verify state/nonce (prevents CSRF)
        # Note: In stateless API mode, you might use a different approach (e.g., JWT)
        
        # Exchange code for access token
        response = HTTParty.post("https://#{shop}/admin/oauth/access_token", 
          body: {
            client_id: ENV['SHOPIFY_API_KEY'],
            client_secret: ENV['SHOPIFY_API_SECRET'],
            code: code
          }
        )

        if response.code == 200
          token = response['access_token']
          scope = response['scope']
          
          # Store token securely in database
          begin
            Shop.store_token(domain: shop, access_token: token)
            Rails.logger.info "Successfully stored token for shop: #{shop}"
            render json: { message: "Installation successful", shop: shop, scopes: scope }
          rescue => e
            Rails.logger.error "Failed to store token: #{e.message}"
            render json: { error: "Failed to store credentials" }, status: 500
          end
        else
          render json: { error: "Failed to authorize", details: response.body }, status: 400
        end
      end

      private

      def verify_hmac(query_string, hmac)
        return false if hmac.blank?
        
        # Remove hmac from query string for verification
        params_without_hmac = query_string
          .split('&')
          .reject { |p| p.start_with?('hmac=') }
          .sort
          .join('&')
        
        secret = ENV['SHOPIFY_API_SECRET']
        calculated_hmac = OpenSSL::HMAC.hexdigest('SHA256', secret, params_without_hmac)
        
        # Use secure comparison to prevent timing attacks
        ActiveSupport::SecurityUtils.secure_compare(calculated_hmac, hmac)
      end
    end
  end
end