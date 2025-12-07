import express from 'express';
import prisma from '../utils/prisma';

const router = express.Router();

// Stats Endpoint for Dashboard Cards
router.get('/stats', async (req, res) => {
    try {
        const postCount = await prisma.post.count();
        const userCount = await prisma.user.count();
        // Mocking other stats for the demo
        res.json({
            dbRecords: postCount + userCount,
            cacheSize: Math.floor(Math.random() * 100),
            computations: Math.floor(Math.random() * 1000),
            activeTasks: Math.floor(Math.random() * 10)
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
});

// Lightweight DB Ping for Latency Check
router.get('/db-ping', async (req, res) => {
    try {
        await prisma.$queryRaw`SELECT 1`;
        res.json({ status: 'ok' });
    } catch (error) {
        res.status(500).json({ error: 'DB Ping Failed' });
    }
});

// CPU Intensive Task - Calculate Primes
router.get('/cpu-intensive', (req, res) => {
    const start = Date.now();
    let count = 0;
    // Run a loop for ~2 seconds
    while (Date.now() - start < 2000) {
        let isPrime = true;
        const num = Math.floor(Math.random() * 10000);
        for (let i = 2; i <= Math.sqrt(num); i++) {
            if (num % i === 0) {
                isPrime = false;
                break;
            }
        }
        if (isPrime) count++;
    }
    res.json({ message: `CPU Task Complete. Found ${count} primes.` });
});

// Memory Intensive Task - Allocate Large Array (Temporary Spike)
router.get('/memory-intensive', (req, res) => {
    const arr = [];
    // Allocate ~100MB of strings
    try {
        for (let i = 0; i < 1000000; i++) {
            arr.push("Memory Test " + i);
        }
        res.json({ message: `Memory Task Complete. Allocated ${arr.length} strings.` });
    } catch (e) {
        res.status(500).json({ error: 'Memory allocation failed' });
    }
});

// Database Intensive Task - Spam Reads
router.get('/database-intensive', async (req, res) => {
    const start = Date.now();
    let count = 0;
    try {
        // Run for ~2 seconds
        while (Date.now() - start < 2000) {
            await prisma.post.findMany({ take: 5 });
            count++;
        }
        res.json({ message: `DB Task Complete. Performed ${count} queries.` });
    } catch (error) {
        res.status(500).json({ error: 'Database task failed' });
    }
});

// Stateful Memory Leak for "Slow" consumption
const memoryStore: string[] = [];

router.get('/stress/memory/grow', (req, res) => {
    // Allocate ~10MB
    const chunk = new Array(1024 * 1024).join('x');
    memoryStore.push(chunk);
    res.json({
        message: 'Allocated 10MB',
        currentSizeMB: memoryStore.length * 10,
        totalChunks: memoryStore.length
    });
});

router.get('/stress/memory/clear', (req, res) => {
    memoryStore.length = 0;
    if (global.gc) { global.gc(); } // Try to force GC if exposed
    res.json({ message: 'Memory cleared', currentSizeMB: 0 });
});

export default router;
