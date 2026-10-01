const mongoose = require("mongoose");
const learningTreeSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true,
    },

    title: {
      type: String,
      required: true,
      trim: true,
    },

    originalQuery: {
      type: String,
      required: true,
    },

    sourceType: {
      type: String,
      enum: ["general", "website"],
      required: true,
    },

    sourceUrl: {
      type: String,
      default: null,
    },

    lastStudiedAt: {
      type: Date,
      default: Date.now,
    },
  },
  { timestamps: true }
);

module.exports = mongoose.model(
  "LearningTree",
  learningTreeSchema
);