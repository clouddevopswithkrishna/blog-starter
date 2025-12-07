import { Request, Response } from 'express';
import { z } from 'zod';
import prisma from '../utils/prisma';

interface AuthRequest extends Request {
    user?: {
        userId: number;
    };
}

const createPostSchema = z.object({
    title: z.string().min(1),
    body: z.string().min(1),
});

const updatePostSchema = z.object({
    title: z.string().min(1).optional(),
    body: z.string().min(1).optional(),
});

export const getPosts = async (req: Request, res: Response) => {
    const posts = await prisma.post.findMany({
        include: { author: { select: { id: true, name: true, email: true } } },
    });
    res.json(posts);
};

export const getPost = async (req: Request, res: Response) => {
    const { id } = req.params;
    const post = await prisma.post.findUnique({
        where: { id: Number(id) },
        include: { author: { select: { id: true, name: true, email: true } } },
    });

    if (!post) {
        return res.status(404).json({ message: 'Post not found' });
    }

    res.json(post);
};

export const createPost = async (req: Request, res: Response) => {
    try {
        const { title, body } = createPostSchema.parse(req.body);
        const userId = (req as AuthRequest).user!.userId;

        const post = await prisma.post.create({
            data: {
                title,
                body,
                authorId: userId,
            },
        });

        res.status(201).json(post);
    } catch (error) {
        if (error instanceof z.ZodError) {
            res.status(400).json({ errors: error.errors });
        } else {
            res.status(500).json({ message: 'Internal server error' });
        }
    }
};

export const updatePost = async (req: Request, res: Response) => {
    try {
        const { id } = req.params;
        const { title, body } = updatePostSchema.parse(req.body);
        const userId = (req as AuthRequest).user!.userId;

        const post = await prisma.post.findUnique({ where: { id: Number(id) } });

        if (!post) {
            return res.status(404).json({ message: 'Post not found' });
        }

        if (post.authorId !== userId) {
            return res.status(403).json({ message: 'Unauthorized' });
        }

        const updatedPost = await prisma.post.update({
            where: { id: Number(id) },
            data: { title, body },
        });

        res.json(updatedPost);
    } catch (error) {
        if (error instanceof z.ZodError) {
            res.status(400).json({ errors: error.errors });
        } else {
            res.status(500).json({ message: 'Internal server error' });
        }
    }
};

export const deletePost = async (req: Request, res: Response) => {
    const { id } = req.params;
    const userId = (req as AuthRequest).user!.userId;

    const post = await prisma.post.findUnique({ where: { id: Number(id) } });

    if (!post) {
        return res.status(404).json({ message: 'Post not found' });
    }

    if (post.authorId !== userId) {
        return res.status(403).json({ message: 'Unauthorized' });
    }

    await prisma.post.delete({ where: { id: Number(id) } });

    res.status(204).send();
};
