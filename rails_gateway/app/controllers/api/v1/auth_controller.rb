module Api
  module V1
    class AuthController < ApplicationController
      
      # Step 1: Redirect user to Shopify Permission Screen
      def install
        shop = params[:shop]
        return render json: { error: "Missing shop parameter" }, status: 400 unless shop

        api_key = ENV['SHOPIFY_API_KEY']
        scopes = 'read_products,read_orders,read_all_orders,read_analytics'
        redirect_uri = 'http://localhost:3000/api/v1/auth/shopify/callback'

        # Construct permission URL
        install_url = "https://#{shop}/admin/oauth/authorize?client_id=#{api_key}&scope=#{scopes}&redirect_uri=#{redirect_uri}"
        
        redirect_to install_url, allow_other_host: true
      end

      # Step 2: Handle Callback and Exchange Code for Token
      def callback
        shop = params[:shop]
        code = params[:code]
        
        # In production, verify HMAC signature here
        
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
          # TODO: Store this token in a database linked to the 'shop' domain
          render json: { message: "Installation successful", token: token, shop: shop }
        else
          render json: { error: "Failed to authorize" }, status: 400
        end
      end
    end
  end
end