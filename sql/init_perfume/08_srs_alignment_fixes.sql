-- ============================================================================
-- 10_srs_alignment_fixes.sql
-- Sub-Phase 12C/12D Alignment Fixes for Payment Adapter & Schema
--
-- Fixes:
--  - Expand payments.method ENUM to include 'simulated' (FR-06, AC-02.1)
--
-- Safety: Non-destructive, re-runnable (runs cleanly multiple times).
-- ============================================================================

USE online_shop_perfume_dev;

-- WHY: Expands payments.method ENUM to allow 'simulated' payment gateway adapter testing (FR-06, AC-02.1).
ALTER TABLE payments 
MODIFY COLUMN method ENUM('cod', 'card', 'bank_transfer', 'wallet', 'simulated') NOT NULL DEFAULT 'cod';

