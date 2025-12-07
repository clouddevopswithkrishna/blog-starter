import { Router } from 'express';
import {
    createPost,
    deletePost,
    getPost,
    getPosts,
    updatePost,
} from '../controllers/postController';
import { authenticate } from '../middleware/auth';

const router = Router();

router.get('/', getPosts);
router.get('/:id', getPost);
router.post('/', authenticate, createPost);
router.put('/:id', authenticate, updatePost);
router.delete('/:id', authenticate, deletePost);

export default router;
