import { useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';

export default function Delete() {
  const router = useRouter();
  
  useEffect(() => {
    // Client-side redirect to the static HTML file
    window.location.href = '/delete.html';
  }, []);

  return (
    <>
      <Head>
        <title>What's Cooking? - Account Deletion</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
      </Head>
      <div>
        <p>Loading...</p>
      </div>
    </>
  );
}
