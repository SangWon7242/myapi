type HelloResponse = {
  message: string;
};

export const dynamic = "force-dynamic";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

async function getHelloMessage(): Promise<string> {
  if (!apiBaseUrl) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not set");
  }

  const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/hello`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch hello message");
  }

  const data = (await response.json()) as HelloResponse;
  return data.message;
}

export default async function Home() {
  const message = await getHelloMessage();

  return (
    <div className="flex flex-1 items-center justify-center text-2xl font-bold">
      {message}
    </div>
  );
}
