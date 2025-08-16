import { useEffect, useRef } from 'react';
import Head from 'next/head';

export default function HTMLRenderer({ htmlContent }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !htmlContent) return;

    // Clear existing content
    containerRef.current.innerHTML = '';

    // Create a temporary element to parse the HTML
    const tempEl = document.createElement('div');
    tempEl.innerHTML = htmlContent;

    // Extract head elements to add to the document head
    const headElements = [];
    const headTags = tempEl.querySelectorAll('head > *');
    headTags.forEach(el => {
      // Skip if it's a script as Next will handle those differently
      if (el.tagName !== 'SCRIPT') {
        headElements.push(el.outerHTML);
      }
    });

    // Add the body content to our container
    const bodyContent = tempEl.querySelector('body');
    if (bodyContent) {
      containerRef.current.innerHTML = bodyContent.innerHTML;
    } else {
      containerRef.current.innerHTML = tempEl.innerHTML;
    }

    // Handle scripts separately to ensure they execute
    const scripts = tempEl.querySelectorAll('script');
    scripts.forEach(oldScript => {
      const newScript = document.createElement('script');
      Array.from(oldScript.attributes).forEach(attr => {
        newScript.setAttribute(attr.name, attr.value);
      });
      newScript.appendChild(document.createTextNode(oldScript.innerHTML));
      document.body.appendChild(newScript);
    });

    // Set document title if present
    const titleTag = tempEl.querySelector('title');
    if (titleTag) {
      document.title = titleTag.textContent;
    }
  }, [htmlContent]);

  return (
    <>
      <Head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div ref={containerRef} />
    </>
  );
}
