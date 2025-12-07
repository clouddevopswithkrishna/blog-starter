import { Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import prisma from '../utils/prisma';

const registerSchema = z.object({
    name: z.string().min(2),
    email: z.string().email(),
    password: z.string().min(6),
});

const loginSchema = z.object({
    email: z.string().email(),
    password: z.string(),
});

export const register = async (req: Request, res: Response) => {
    try {
        const { name, email, password } = registerSchema.parse(req.body);

        const existingUser = await prisma.user.findUnique({ where: { email } });
        if (existingUser) {
            return res.status(400).json({ message: 'User already exists' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);

        const user = await prisma.user.create({
            data: {
                name,
                email,
                password: hashedPassword,
            },
        });

        const token = jwt.sign({ userId: user.id, name: user.name, email: user.email }, process.env.JWT_SECRET || 'secret', {
            expiresIn: '1d',
        });

        res.status(201).json({
            id: user.id,
            name: user.name,
            email: user.email,
            token,
        });
    } catch (error) {
        if (error instanceof z.ZodError) {
            res.status(400).json({ errors: error.errors });
        } else {
            res.status(500).json({ message: 'Internal server error' });
        }
    }
};

export const login = async (req: Request, res: Response) => {
    try {
        const { email, password } = loginSchema.parse(req.body);

        const user = await prisma.user.findUnique({ where: { email } });
        if (!user) {
            return res.status(400).json({ message: 'Invalid credentials' });
        }

        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(400).json({ message: 'Invalid credentials' });
        }

        const token = jwt.sign({ userId: user.id, name: user.name, email: user.email }, process.env.JWT_SECRET || 'secret', {
            expiresIn: '1d',
        });

        res.json({ token });
    } catch (error) {
        if (error instanceof z.ZodError) {
            res.status(400).json({ errors: error.errors });
        } else {
            res.status(500).json({ message: 'Internal server error' });
        }
    }
};
