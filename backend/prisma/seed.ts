import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
    const password = await bcrypt.hash('password123', 10);

    const user1 = await prisma.user.upsert({
        where: { email: 'alice@example.com' },
        update: {},
        create: {
            email: 'alice@example.com',
            name: 'Alice',
            password,
            posts: {
                create: [
                    {
                        title: 'Hello World',
                        body: 'This is my first post',
                    },
                    {
                        title: 'Second Post',
                        body: 'More content here',
                    },
                ],
            },
        },
    });

    const user2 = await prisma.user.upsert({
        where: { email: 'bob@example.com' },
        update: {},
        create: {
            email: 'bob@example.com',
            name: 'Bob',
            password,
            posts: {
                create: [
                    {
                        title: 'Bob\'s Thoughts',
                        body: 'I like blogging too',
                    },
                    {
                        title: 'Another one',
                        body: 'Prisma is cool',
                    },
                ],
            },
        },
    });

    console.log({ user1, user2 });
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
