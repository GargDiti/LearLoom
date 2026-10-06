import mongoose from "mongoose";
const conversationSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
      required: true,
      index: true,
    },

    title: {
      type: String,
      default: "New Conversation",
      trim: true,
    },
    sourceUrl: {
      type: String,
      default: null,
      trim: true,
    },
    availableTopics: {
      type: [mongoose.Schema.Types.Mixed],
      default: [],
    },
    awaitingTopicSelection: {
      type: Boolean,
      default: false,
    },
    allowWholeWebsite: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
  }
);

const Conversation = mongoose.model(
  "Conversation",
  conversationSchema
);

export default Conversation;