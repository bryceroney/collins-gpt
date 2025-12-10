import { MessageSquareText } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

export const metadata = {
  title: "DixerWriter - CollinsGPT",
  description: "Generate House of Representatives question time dixers",
}

export default function DixerWriterPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <MessageSquareText className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
              DixerWriter
            </h1>
            <p className="text-muted-foreground">
              Question Time Dixer Generator
            </p>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>About this tool</CardTitle>
          <CardDescription>
            Takes a media release and writes a House of Representatives question time dixer in the Minister's style.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border-2 border-dashed border-muted-foreground/25 p-8 text-center">
            <p className="text-muted-foreground">
              Tool interface coming soon
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
