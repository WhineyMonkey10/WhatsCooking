import { useEffect } from 'react';
import fs from 'fs';
import path from 'path';
import HTMLRenderer from '../components/HTMLRenderer';

export default function Home({ htmlContent }) {
  return <HTMLRenderer htmlContent={htmlContent} />;
}

// This gets called at build time
export async function getStaticProps() {
  const filePath = path.join(process.cwd(), 'index.html');
  const htmlContent = fs.readFileSync(filePath, 'utf8');
  
  return {
    props: {
      htmlContent,
    },
  };
}
