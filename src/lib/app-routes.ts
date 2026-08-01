import {
  Building2,
  ChartNoAxesCombined,
  FolderKanban,
  Globe2,
  Package,
  Settings,
  Wrench,
  Boxes,
  type LucideIcon,
} from "lucide-react";

export type AppRouteGroup = "workspace" | "ecosystem";

export type AppRouteId =
  | "overview"
  | "store"
  | "versions"
  | "maintenance"
  | "environmentSettings"
  | "remoteWsl"
  | "containers"
  | "privateRegistry";

export type AppRoute = {
  id: AppRouteId;
  group: AppRouteGroup;
  path: string;
  title: string;
  navLabel: string;
  description: string;
  icon: LucideIcon;
  scope: string;
  items: string[];
};

export const appRoutes: AppRoute[] = [
  {
    id: "overview",
    group: "workspace",
    path: "/",
    title: "概览看板",
    navLabel: "概览看板",
    description: "汇总环境状态、安装概况和最近维护动作。",
    icon: ChartNoAxesCombined,
    scope: "主页 / 仪表盘",
    items: ["环境状态总览", "已安装版本统计", "最近操作记录"],
  },
  {
    id: "store",
    group: "workspace",
    path: "/store",
    title: "环境商店",
    navLabel: "环境商店",
    description: "以安装卡片形式展示可安装环境。",
    icon: Package,
    scope: "安装卡片",
    items: ["环境搜索", "安装入口", "镜像源适配"],
  },
  {
    id: "versions",
    group: "workspace",
    path: "/versions",
    title: "版本管理",
    navLabel: "版本管理",
    description: "管理环境系列、已安装版本和默认软链接切换。",
    icon: FolderKanban,
    scope: "系列面板 + 切换软链接",
    items: ["版本系列分组", "默认版本切换", "软链接状态检查"],
  },
  {
    id: "maintenance",
    group: "workspace",
    path: "/maintenance",
    title: "维护中心",
    navLabel: "维护中心",
    description: "集中处理卸载、清理、备份与恢复。",
    icon: Wrench,
    scope: "卸载 + 备份恢复",
    items: ["环境卸载", "备份创建", "恢复入口"],
  },
  {
    id: "environmentSettings",
    group: "workspace",
    path: "/environment-settings",
    title: "环境设置",
    navLabel: "环境设置",
    description: "配置环境默认项、镜像源和软链接目录。",
    icon: Settings,
    scope: "全局配置 / 镜像源 / 软链接默认目录",
    items: ["默认安装目录", "镜像源配置", "软链接默认目录"],
  },
  {
    id: "remoteWsl",
    group: "ecosystem",
    path: "/remote-wsl",
    title: "远程与 WSL",
    navLabel: "远程与 WSL",
    description: "管理远程主机、WSL 发行版和跨环境连接。",
    icon: Globe2,
    scope: "界面已做 / 逻辑待实现",
    items: ["远程主机连接", "WSL 发行版", "环境同步状态"],
  },
  {
    id: "containers",
    group: "ecosystem",
    path: "/containers",
    title: "容器管理",
    navLabel: "容器管理",
    description: "集中查看容器运行态、镜像和开发环境映射。",
    icon: Boxes,
    scope: "界面已做 / 逻辑待实现",
    items: ["容器运行态", "镜像管理", "端口与目录映射"],
  },
  {
    id: "privateRegistry",
    group: "ecosystem",
    path: "/private-registry",
    title: "私有源仓库",
    navLabel: "私有源仓库",
    description: "管理组织内部源、认证信息和环境包索引。",
    icon: Building2,
    scope: "界面已做 / 逻辑待实现",
    items: ["仓库地址", "认证配置", "包索引同步"],
  },
];

export const workspaceRoutes = appRoutes.filter((route) => route.group === "workspace");
export const ecosystemRoutes = appRoutes.filter((route) => route.group === "ecosystem");

export function getAppRoute(id: AppRouteId) {
  return appRoutes.find((route) => route.id === id) ?? appRoutes[0];
}

export function getAppRouteByPath(pathname: string) {
  return appRoutes.find((route) => route.path === pathname) ?? appRoutes[0];
}
