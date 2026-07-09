import { MESSAGES } from "@/constants/messages"

export const getMessage = (
  code: keyof typeof MESSAGES,
  ...params: string[]
): string => {
  let message = MESSAGES[code] ?? "UNKNOWN MESSAGE"

  params.forEach((param, index) => {
    message = message.replaceAll(`{${index}}`, param)
  })

  return message
}