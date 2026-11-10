import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const project = defineCollection({
  loader: glob({ base: './src/content/projects', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string().min(3),
    summary: z.string().min(20),
    category: z.enum(['software', 'research', 'automation', 'network', 'electrical', 'business']),
    typeLabel: z.string().min(3),
    tags: z.array(z.string().min(1)).min(1),
    order: z.number().int().nonnegative().default(100),
    draft: z.boolean().default(true),
    featured: z.boolean().default(false),
    year: z.number().int().min(1900).max(2100).optional(),
    externalUrl: z.url().optional()
  })
});

const publication = defineCollection({
  loader: glob({ base: './src/content/publications', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string().min(3),
    summary: z.string().min(20),
    type: z.enum(['rapport', 'artikel', 'opgave', 'andet']),
    tags: z.array(z.string().min(1)).min(1),
    authors: z.array(z.string().min(1)).optional(),
    date: z.coerce.date().optional(),
    project: z.string().optional(),
    pdf: z.string().regex(/^\/documents\/[a-z0-9/_-]+\.pdf$/).optional(),
    externalUrl: z.url().optional(),
    draft: z.boolean().default(true),
    featured: z.boolean().default(false),
    order: z.number().int().nonnegative().default(100)
  })
});
export const collections = { projects: project, publications: publication };
