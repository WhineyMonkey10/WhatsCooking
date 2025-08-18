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

    // Execute scripts after a small delay to ensure DOM elements are fully loaded
    setTimeout(() => {
      try {
        // Handle scripts separately to ensure they execute
        const scripts = tempEl.querySelectorAll('script');
        if (scripts && scripts.length > 0) {
          // Convert NodeList to Array for safer handling
          Array.from(scripts).forEach(oldScript => {
            try {
              const newScript = document.createElement('script');
              // Copy attributes
              if (oldScript.attributes && oldScript.attributes.length > 0) {
                Array.from(oldScript.attributes).forEach(attr => {
                  newScript.setAttribute(attr.name, attr.value);
                });
              }
              
              // Handle inline scripts
              if (oldScript.innerHTML) {
                // Wrap in IIFE to prevent global variable conflicts
                const safeContent = `
                  (function() { 
                    ${oldScript.innerHTML}
                  })();
                `;
                newScript.text = safeContent;
              }
              
              // Append to document
              document.body.appendChild(newScript);
            } catch (scriptError) {
              console.error('Error processing script:', scriptError);
            }
          });
        }
      } catch (error) {
        console.error('Error processing scripts:', error);
      }
    }, 100); // Small delay to ensure DOM is ready

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
