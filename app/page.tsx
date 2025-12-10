import Link from "next/link"
import { FileSearch, MessageSquareText, ArrowRight } from "lucide-react"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"

const apps = [
  {
    title: "HIBUpdater",
    description: "Searches the web and checks if any Hot Issues Briefs need updating",
    href: "/hib-updater",
    icon: FileSearch,
  },
  {
    title: "DixerWriter",
    description: "Takes a media release and writes a House of Representatives question time dixer in the Minister's style",
    href: "/dixer-writer",
    icon: MessageSquareText,
  },
]

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="mb-8 md:mb-12">
        <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
          Welcome to CollinsGPT
        </h1>
        <p className="mt-2 text-muted-foreground">
          AI-powered tools for the office of Minister Julie Collins
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {apps.map((app) => (
          <Link key={app.href} href={app.href} className="group">
            <Card className="h-full transition-colors hover:border-primary/50">
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <app.icon className="h-5 w-5 text-primary" />
                </div>
                <CardTitle className="flex items-center gap-2">
                  {app.title}
                  <ArrowRight className="h-4 w-4 opacity-0 transition-opacity group-hover:opacity-100" />
                </CardTitle>
                <CardDescription>{app.description}</CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
