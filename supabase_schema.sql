-- Run this in Supabase SQL Editor to create tables for LLM Tracker.

-- Table: projects
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Table: runs
CREATE TABLE runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  model_name TEXT NOT NULL,
  prompt TEXT NOT NULL,
  response TEXT NOT NULL,
  latency FLOAT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for dashboard queries
CREATE INDEX idx_runs_project_created ON runs(project_id, created_at DESC);
