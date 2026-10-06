import Conversation from "../models/conversation.js";
import Message from "../models/message.js";
import mongoose from "mongoose";
import aiService from "../services/aiService.js";

const MAX_MESSAGE_LENGTH = 20000;
const MAX_HISTORY_MESSAGES = 10;

function isValidConversationId(id) {
  return mongoose.Types.ObjectId.isValid(id);
}

async function findOwnedConversation(id, userId) {
  if (!isValidConversationId(id)) {
    return { error: "invalid" };
  }

  const conversation = await Conversation.findOne({ _id: id, userId });
  return conversation ? { conversation } : { error: "not_found" };
}

// Create a new conversation
const createConversation = async (req, res) => {
  try {
    const requestedTitle = req.body?.title;
    if (requestedTitle !== undefined && typeof requestedTitle !== "string") {
      return res.status(400).json({ success: false, message: "Title must be text" });
    }

    const conversation = await Conversation.create({
      userId: req.user.id,
      title: requestedTitle?.trim().slice(0, 120) || "New Conversation",
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

const getConversation = async (req, res) => {
  try {
    const found = await findOwnedConversation(req.params.id, req.user.id);
    if (found.error === "invalid") {
      return res.status(400).json({ success: false, message: "Invalid conversation ID" });
    }
    if (!found.conversation) {
      return res.status(404).json({ success: false, message: "Conversation not found" });
    }

    const messages = await Message.find({ conversationId: found.conversation._id })
      .sort({ createdAt: 1, _id: 1 });
    return res.status(200).json({
      success: true,
      conversation: found.conversation,
      messages,
    });
  } catch (error) {
    console.error("[CONVERSATION] Could not fetch conversation:", error.message);
    return res.status(500).json({ success: false, message: "Failed to fetch conversation" });
  }
};

const deleteConversation = async (req, res) => {
  try {
    const found = await findOwnedConversation(req.params.id, req.user.id);
    if (found.error === "invalid") {
      return res.status(400).json({ success: false, message: "Invalid conversation ID" });
    }
    if (!found.conversation) {
      return res.status(404).json({ success: false, message: "Conversation not found" });
    }

    await Message.deleteMany({ conversationId: found.conversation._id });
    await Conversation.deleteOne({ _id: found.conversation._id, userId: req.user.id });
    return res.status(200).json({ success: true, message: "Conversation deleted" });
  } catch (error) {
    console.error("[CONVERSATION] Could not delete conversation:", error.message);
    return res.status(500).json({ success: false, message: "Failed to delete conversation" });
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
    if (!isValidConversationId(id)) {
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

const sendMessage = async (req, res) => {
  try {
    const { id } = req.params;
    const content = req.body?.message;
    if (typeof content !== "string" || !content.trim()) {
      return res.status(400).json({ success: false, message: "Message cannot be empty" });
    }
    if (content.trim().length > MAX_MESSAGE_LENGTH) {
      return res.status(400).json({
        success: false,
        message: `Message cannot exceed ${MAX_MESSAGE_LENGTH} characters`,
      });
    }

    const found = await findOwnedConversation(id, req.user.id);
    if (found.error === "invalid") {
      return res.status(400).json({ success: false, message: "Invalid conversation ID" });
    }
    if (!found.conversation) {
      return res.status(404).json({ success: false, message: "Conversation not found" });
    }

    const conversation = found.conversation;
    console.log(`[CONVERSATION] Conversation found: ${conversation._id}`);
    const userMessage = await Message.create({
      conversationId: conversation._id,
      role: "user",
      content: content.trim(),
    });
    console.log(`[MESSAGE] User message saved: ${userMessage._id}`);

    const previousMessages = await Message.find({
      conversationId: conversation._id,
      _id: { $ne: userMessage._id },
    })
      .sort({ createdAt: -1, _id: -1 })
      .limit(MAX_HISTORY_MESSAGES)
      .lean();
    const conversationHistory = previousMessages.reverse().map(({ role, content: text }) => ({
      role,
      content: text,
    }));
    console.log(`[HISTORY] Previous messages retrieved: ${conversationHistory.length}`);

    let aiResult;
    try {
      console.log("[AI] Sending request to FastAPI");
      aiResult = await aiService.generateAnswer({
        query: content.trim(),
        conversationHistory,
        sourceUrl: conversation.sourceUrl,
      });
      console.log("[AI] Response received");
    } catch (error) {
      console.error("[AI] FastAPI request failed:", error.message);
      return res.status(502).json({
        success: false,
        message: "The AI service could not generate a response",
        userMessage,
      });
    }

    const assistantMessage = await Message.create({
      conversationId: conversation._id,
      role: "assistant",
      content: aiResult.result.trim(),
    });
    console.log(`[MESSAGE] Assistant message saved: ${assistantMessage._id}`);

    const updates = {};
    if (conversation.title === "New Conversation") {
      updates.title = content.trim().slice(0, 120);
    }
    if (aiResult.url && !conversation.sourceUrl) {
      updates.sourceUrl = aiResult.url;
    }
    if (Object.keys(updates).length) {
      await Conversation.updateOne({ _id: conversation._id }, { $set: updates });
    } else {
      await Conversation.updateOne({ _id: conversation._id }, { $set: { updatedAt: new Date() } });
    }

    return res.status(200).json({
      success: true,
      conversationId: conversation._id,
      message: assistantMessage,
    });
  } catch (error) {
    console.error("[MESSAGE] Could not process message:", error.message);
    return res.status(500).json({ success: false, message: "Failed to process message" });
  }
};

export {
  createConversation,
  getConversations,
  getConversation,
  deleteConversation,
  getMessages,
  sendMessage,
};
