import Conversation from "../models/conversation.js";
import Message from "../models/message.js";
import mongoose from "mongoose";


// Create a new conversation
const createConversation = async (req, res) => {
  try {
    const conversation = await Conversation.create({
      userId: req.user.id,
      title: "New Conversation",
    });

    res.status(201).json({
      success: true,
      conversation,
    });
  } catch (error) {
    console.error("Create conversation error:", error.message);
    res.status(500).json({
      success: false,
      message: "Failed to create conversation",
    });
  }
};

// Get all conversations of the logged-in user
const getConversations = async (req, res) => {
  try {
    const conversations = await Conversation.find({
      userId: req.user.id,
    }).sort({ updatedAt: -1 });

    res.status(200).json({
      success: true,
      conversations,
    });
  } catch (error) {
    console.error("Get conversations error:", error.message);
    res.status(500).json({
      success: false,
      message: "Failed to fetch conversations",
    });
  }
};

//get messages
const getMessages = async (req, res) => {
  try {
    const { id } = req.params;

    // Validate the conversation ID
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({
        success: false,
        message: "Invalid conversation ID",
      });
    }

    // Check that the conversation belongs to this user
    const conversation = await Conversation.findOne({
      _id: id,
      userId: req.user.id,
    });

    if (!conversation) {
      return res.status(404).json({
        success: false,
        message: "Conversation not found",
      });
    }

    // Retrieve messages in chronological order
    const messages = await Message.find({
      conversationId: conversation._id,
    }).sort({ createdAt: 1 });

    return res.status(200).json({
      success: true,
      messages,
    });
  } catch (error) {
    console.error("Get messages error:", error.message);

    return res.status(500).json({
      success: false,
      message: "Failed to fetch messages",
    });
  }
};

export {
  createConversation,
  getConversations,
  getMessages,
};
