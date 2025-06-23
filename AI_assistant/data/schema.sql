-- Trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

-- USERS
CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "email" varchar UNIQUE NOT NULL,
  "phone_number" varchar UNIQUE,
  "hashed_password" varchar NOT NULL,
  "tier" varchar,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON "users"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- USER PREFERENCES
CREATE TABLE "user_preferences" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid UNIQUE NOT NULL,
  "preferences" jsonb,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER set_timestamp_user_preferences
BEFORE UPDATE ON "user_preferences"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- CHAT SESSIONS
CREATE TABLE "chat_sessions" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "session_type" varchar,
  "started_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "ended_at" timestamp
);

-- MESSAGES
CREATE TABLE "messages" (
  "id" uuid PRIMARY KEY,
  "session_id" uuid NOT NULL,
  "sender" varchar,
  "message" text,
  "response_to" uuid,
  "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- PLANS
CREATE TABLE "plans" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "description" text,
  "price" numeric(10,2),
  "billing_cycle" varchar,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER set_timestamp_plans
BEFORE UPDATE ON "plans"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- SUBSCRIPTIONS
CREATE TABLE "subscriptions" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "plan_id" uuid NOT NULL,
  "status" varchar,
  "start_date" date,
  "end_date" date,
  "trial_end_date" date,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER set_timestamp_subscriptions
BEFORE UPDATE ON "subscriptions"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- PAYMENTS
CREATE TABLE "payments" (
  "id" uuid PRIMARY KEY,
  "subscription_id" uuid NOT NULL,
  "amount" numeric(10,2),
  "currency" varchar,
  "payment_date" timestamp,
  "payment_method" varchar,
  "status" varchar,
  "provider_payment_id" varchar UNIQUE,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- AI REQUESTS
CREATE TABLE "ai_requests" (
  "id" uuid PRIMARY KEY,
  "session_id" uuid NOT NULL,
  "prompt" text,
  "response" text,
  "model_used" varchar,
  "tokens_used" integer,
  "latency_ms" integer,
  "temperature" float,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- AI SUMMARY CACHE
CREATE TABLE "ai_summary_cache" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "summary_type" varchar,
  "content" jsonb,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- TRIPS
CREATE TABLE "trips" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "name" varchar,
  "destination" varchar,
  "start_date" date,
  "end_date" date,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER set_timestamp_trips
BEFORE UPDATE ON "trips"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ITINERARIES
CREATE TABLE "itineraries" (
  "id" uuid PRIMARY KEY,
  "trip_id" uuid NOT NULL,
  "day" integer,
  "activities" jsonb,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER set_timestamp_itineraries
BEFORE UPDATE ON "itineraries"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- AFFILIATES
CREATE TABLE "affiliates" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "partner_url" varchar,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER set_timestamp_affiliates
BEFORE UPDATE ON "affiliates"
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- AFFILIATE CLICKS
CREATE TABLE "affiliate_clicks" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "affiliate_id" uuid NOT NULL,
  "destination_url" varchar,
  "clicked_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Comments
COMMENT ON COLUMN "users"."phone_number" IS 'Optional';
COMMENT ON COLUMN "users"."tier" IS 'ENUM: free, pro';
COMMENT ON COLUMN "chat_sessions"."session_type" IS 'ENUM: chat, form, wizard';
COMMENT ON COLUMN "messages"."sender" IS 'ENUM: user, assistant, system';
COMMENT ON COLUMN "plans"."billing_cycle" IS 'ENUM: monthly, yearly';
COMMENT ON COLUMN "subscriptions"."status" IS 'ENUM: active, cancelled, past_due, trial';
COMMENT ON COLUMN "payments"."payment_method" IS 'e.g., card, paypal';
COMMENT ON COLUMN "payments"."status" IS 'ENUM: success, failed, pending';
COMMENT ON COLUMN "payments"."provider_payment_id" IS 'From external provider';
COMMENT ON COLUMN "ai_summary_cache"."summary_type" IS 'ENUM: preference, trip, chat';
COMMENT ON COLUMN "messages"."response_to" IS 'Refers to the message this is responding to';

-- Foreign Keys
ALTER TABLE "user_preferences" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
ALTER TABLE "chat_sessions" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
ALTER TABLE "messages" ADD FOREIGN KEY ("session_id") REFERENCES "chat_sessions" ("id");
ALTER TABLE "messages" ADD FOREIGN KEY ("response_to") REFERENCES "messages" ("id");
ALTER TABLE "subscriptions" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
ALTER TABLE "subscriptions" ADD FOREIGN KEY ("plan_id") REFERENCES "plans" ("id");
ALTER TABLE "payments" ADD FOREIGN KEY ("subscription_id") REFERENCES "subscriptions" ("id");
ALTER TABLE "ai_requests" ADD FOREIGN KEY ("session_id") REFERENCES "chat_sessions" ("id");
ALTER TABLE "ai_summary_cache" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
ALTER TABLE "trips" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
ALTER TABLE "itineraries" ADD FOREIGN KEY ("trip_id") REFERENCES "trips" ("id");
ALTER TABLE "affiliate_clicks" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
ALTER TABLE "affiliate_clicks" ADD FOREIGN KEY ("affiliate_id") REFERENCES "affiliates" ("id");
