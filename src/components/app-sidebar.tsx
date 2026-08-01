import { ChevronsUpDown, LogOut, Sparkles, UserRound } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import type { AppRoute } from "@/lib/app-routes";

type AppSidebarProps = {
  workspaceRoutes: AppRoute[];
  ecosystemRoutes: AppRoute[];
  activePath: string;
};

const sidebarUser = {
  name: "Guest User",
  email: "guest@wingenv.local",
  initials: "GU",
};

function RouteGroup({
  label,
  routes,
  activePath,
}: {
  label: string;
  routes: AppRoute[];
  activePath: string;
}) {
  return (
    <SidebarGroup>
      <SidebarGroupLabel>{label}</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {routes.map((route) => {
            const Icon = route.icon;
            const isActive = route.path === activePath;

            return (
              <SidebarMenuItem key={route.id}>
                <SidebarMenuButton
                  asChild
                  tooltip={route.navLabel}
                  isActive={isActive}
                  className={cn(isActive && "font-medium")}
                >
                  <a href={route.path}>
                    <Icon />
                    <span>{route.navLabel}</span>
                  </a>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}

function SidebarUserMenu() {
  const { isMobile } = useSidebar();

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg text-xs font-semibold">
                {sidebarUser.initials}
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">{sidebarUser.name}</span>
                <span className="text-muted-foreground truncate text-xs">{sidebarUser.email}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg text-xs font-semibold">
                  {sidebarUser.initials}
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">{sidebarUser.name}</span>
                  <span className="text-muted-foreground truncate text-xs">
                    {sidebarUser.email}
                  </span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem>
                <UserRound />
                用户中心
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Sparkles />
                升级用户
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <LogOut />
              退出登录
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}

export function AppSidebar({ workspaceRoutes, ecosystemRoutes, activePath }: AppSidebarProps) {
  return (
    <Sidebar collapsible="icon" className="top-8 h-[calc(100svh-2rem)]">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" tooltip="WingEnv">
              <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg text-sm font-semibold">
                WE
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">WingEnv</span>
                <span className="text-muted-foreground truncate text-xs">Environment Manager</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <RouteGroup label="工作台" routes={workspaceRoutes} activePath={activePath} />
        <RouteGroup label="高级生态" routes={ecosystemRoutes} activePath={activePath} />
      </SidebarContent>

      <SidebarFooter>
        <SidebarUserMenu />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
