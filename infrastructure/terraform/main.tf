terraform {
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}

variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "us-central1"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "raw" {
  name                        = "${var.project_id}-retailpulse-raw"
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "warehouse" {
  dataset_id = "retailpulse"
  location   = var.region
}

resource "google_pubsub_topic" "events" {
  name = "retail-events"
}
