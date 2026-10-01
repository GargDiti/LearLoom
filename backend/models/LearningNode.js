import mongoose from "mongoose";

const learningNodeSchema = new mongoose.Schema(
  {
    treeId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "LearningTree",
      required: true,
      index: true,
    },

    parentId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "LearningNode",
      default: null,
    },

    title: {
      type: String,
      required: true,
      trim: true,
    },

    type: {
      type: String,
      enum: ["topic", "question", "practice"],
      default: "topic",
    },

    content: {
      type: String,
      default: "",
    },

    status: {
      type: String,
      enum: ["not_started", "in_progress", "completed"],
      default: "not_started",
    },
  },
  { timestamps: true }
);

learningNodeSchema.index({ treeId: 1, parentId: 1 });

const LearningNode = mongoose.model(
  "LearningNode",
  learningNodeSchema
);

export default LearningNode;