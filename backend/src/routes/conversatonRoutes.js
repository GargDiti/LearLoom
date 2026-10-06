import { Router } from "express";
import {
  createConversation,
  getConversations,
  getConversation,
  deleteConversation,
  getMessages,
  sendMessage,
} from "../controllers/conversationController.js";
import authMiddleware from "../middleware/authmiddleware.js";

const router = Router();

router.post("/", authMiddleware, createConversation);
router.get("/", authMiddleware, getConversations);
router.get("/:id", authMiddleware, getConversation);
router.delete("/:id", authMiddleware, deleteConversation);
router.get("/:id/messages", authMiddleware, getMessages);
router.post("/:id/messages", authMiddleware, sendMessage);

export default router;