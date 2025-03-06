# AI Shopping Assistant Frontend

This is the frontend for the AI-powered e-commerce shopping assistant. It provides a conversational interface for users to shop using natural language.

## Technologies Used

- **Next.js**: React framework for building the user interface
- **TypeScript**: For type-safe code
- **Tailwind CSS**: For styling
- **Axios**: For API requests

## Getting Started

1. Install dependencies:

```bash
npm install
```

2. Create a `.env.local` file with the following content:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Features

- Conversational shopping interface
- Product search and recommendations
- Product details view
- Shopping cart functionality
- Checkout process

## Project Structure

- `app/`: Next.js app router pages and components
  - `page.tsx`: Home page
  - `chat/`: Chat interface
  - `about/`: About page
  - `api/`: API service for backend communication
- `public/`: Static assets

## Building for Production

```bash
npm run build
```

Then, you can start the production server:

```bash
npm start
```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
