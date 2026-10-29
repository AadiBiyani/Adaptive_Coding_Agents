let requestToken = ""

export async function bootstrap() {
  const response = await fetch("/api/bootstrap", { cache: "no-store" })
  if (!response.ok) throw new Error("Could not connect to the local agent server.")
  const data = await response.json()
  requestToken = data.token
  return data
}

export async function api(path, body) {
  const response = await fetch(`/api${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: { "X-ACA-Token": requestToken, ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    cache: "no-store",
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || "The local request failed.")
  return data
}

export function modelName(model) {
  return { "gpt-6-luna": "GPT-6 Luna", "gpt-6.1-sol": "GPT-6.1 Sol" }[model] || model || "Auto"
}

export function money(value) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return "Unavailable"
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 4, maximumFractionDigits: 6 }).format(Number(value))
}

export function shortDate(value) {
  return value ? new Date(value).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }) : "Unknown time"
}
