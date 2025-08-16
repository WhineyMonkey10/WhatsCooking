// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

export default function handler(req, res) {
  // get all the client-safe appwrite configuration
  const appwriteConfig = {
    endpoint: process.env.APPWRITE_ENDPOINT,
    project: process.env.APPWRITE_PROJECT,
    database: process.env.APPWRITE_DATABASE,
    collection: process.env.APPWRITE_PUBLIC_COLLECTION,
    deleteFunctionId: process.env.APPWRITE_ACCOUNT_DELETION_FUNCTION_ID,
  };

  // send back the appwrite things that are safe to be sent to the client.
  const safeConfig = Object.fromEntries(
    Object.entries(appwriteConfig).filter(([_, v]) => v !== undefined && v !== null && v !== '')
  );

  if (Object.keys(safeConfig).length !== Object.keys(appwriteConfig).length) {
    console.warn('Some appwrite env vars are missing or empty; sent subset:', safeConfig);
  } else {
    console.log('Sending appwrite config:', safeConfig);
  }

  res.status(200).json(safeConfig);
}
