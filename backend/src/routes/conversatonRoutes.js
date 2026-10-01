import { Router } from "express";
import {
  createConversation,
  getConversations,
  getMessages
} from "../controllers/conversationController.js";
import authMiddleware from "../middleware/authmiddleware.js";

const router = Router();

router.post("/", authMiddleware, createConversation);
router.get("/", authMiddleware, getConversations);
router.get("/:id/messages", authMiddleware, getMessages);

export default router;