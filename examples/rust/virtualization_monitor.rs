//! 虚拟化性能监控器
//! 
//! 这是一个用Rust实现的虚拟化性能监控器，用于监控ESXi主机和虚拟机的性能指标。
//! 该实现展示了虚拟化技术的实际应用，包括性能监控、资源管理和自动化运维。

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use std::thread;
use std::sync::atomic::{AtomicU64, AtomicBool, Ordering};
use serde::{Deserialize, Serialize};
use tokio::time::interval;
use anyhow::{Result, Context};

/// 虚拟化性能指标
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VirtualizationMetrics {
    /// 主机ID
    pub host_id: String,
    /// 时间戳
    pub timestamp: u64,
    /// CPU使用率
    pub cpu_usage: f64,
    /// 内存使用率
    pub memory_usage: f64,
    /// 存储I/O
    pub storage_io: StorageMetrics,
    /// 网络I/O
    pub network_io: NetworkMetrics,
    /// 虚拟机数量
    pub vm_count: u32,
    /// 活跃虚拟机数量
    pub active_vm_count: u32,
    /// 资源分配率
    pub resource_allocation: ResourceAllocation,
}

/// 存储性能指标
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StorageMetrics {
    /// 读取IOPS
    pub read_iops: u64,
    /// 写入IOPS
    pub write_iops: u64,
    /// 读取延迟(ms)
    pub read_latency: f64,
    /// 写入延迟(ms)
    pub write_latency: f64,
    /// 存储使用率
    pub usage_percentage: f64,
}

/// 网络性能指标
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkMetrics {
    /// 入站带宽(Mbps)
    pub inbound_bandwidth: f64,
    /// 出站带宽(Mbps)
    pub outbound_bandwidth: f64,
    /// 入站包数
    pub inbound_packets: u64,
    /// 出站包数
    pub outbound_packets: u64,
    /// 网络延迟(ms)
    pub latency: f64,
}

/// 资源分配信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceAllocation {
    /// CPU分配率
    pub cpu_allocation: f64,
    /// 内存分配率
    pub memory_allocation: f64,
    /// 存储分配率
    pub storage_allocation: f64,
    /// 网络分配率
    pub network_allocation: f64,
}

/// 虚拟机信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VirtualMachine {
    /// 虚拟机ID
    pub vm_id: String,
    /// 虚拟机名称
    pub name: String,
    /// 状态
    pub status: VMStatus,
    /// CPU使用率
    pub cpu_usage: f64,
    /// 内存使用率
    pub memory_usage: f64,
    /// 存储使用量(GB)
    pub storage_used: f64,
    /// 网络使用量(MB)
    pub network_used: f64,
    /// 运行时间(秒)
    pub uptime: u64,
}

/// 虚拟机状态
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VMStatus {
    Running,
    Stopped,
    Suspended,
    Migrating,
    Error,
}

/// ESXi主机信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ESXiHost {
    /// 主机ID
    pub host_id: String,
    /// 主机名称
    pub name: String,
    /// IP地址
    pub ip_address: String,
    /// 总CPU核心数
    pub total_cpu_cores: u32,
    /// 总内存(GB)
    pub total_memory_gb: u64,
    /// 总存储(GB)
    pub total_storage_gb: u64,
    /// 虚拟机列表
    pub virtual_machines: Vec<VirtualMachine>,
    /// 最后更新时间
    pub last_updated: u64,
}

/// 虚拟化监控器
pub struct VirtualizationMonitor {
    /// 主机列表
    hosts: Arc<Mutex<HashMap<String, ESXiHost>>>,
    /// 性能指标历史
    metrics_history: Arc<Mutex<Vec<VirtualizationMetrics>>>,
    /// 监控状态
    is_monitoring: AtomicBool,
    /// 监控间隔(秒)
    monitoring_interval: u64,
    /// 最大历史记录数
    max_history_size: usize,
}

impl VirtualizationMonitor {
    /// 创建新的虚拟化监控器
    pub fn new(monitoring_interval: u64, max_history_size: usize) -> Self {
        Self {
            hosts: Arc::new(Mutex::new(HashMap::new())),
            metrics_history: Arc::new(Mutex::new(Vec::new())),
            is_monitoring: AtomicBool::new(false),
            monitoring_interval,
            max_history_size,
        }
    }

    /// 添加ESXi主机
    pub fn add_host(&self, host: ESXiHost) -> Result<()> {
        let mut hosts = self.hosts.lock().unwrap();
        hosts.insert(host.host_id.clone(), host);
        Ok(())
    }

    /// 移除ESXi主机
    pub fn remove_host(&self, host_id: &str) -> Result<()> {
        let mut hosts = self.hosts.lock().unwrap();
        hosts.remove(host_id);
        Ok(())
    }

    /// 开始监控
    pub async fn start_monitoring(&self) -> Result<()> {
        if self.is_monitoring.load(Ordering::Relaxed) {
            return Err(anyhow::anyhow!("监控已在运行"));
        }

        self.is_monitoring.store(true, Ordering::Relaxed);
        
        let hosts = Arc::clone(&self.hosts);
        let metrics_history = Arc::clone(&self.metrics_history);
        let is_monitoring = Arc::new(self.is_monitoring.clone());
        let interval_duration = self.monitoring_interval;

        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(interval_duration));
            
            while is_monitoring.load(Ordering::Relaxed) {
                interval.tick().await;
                
                // 收集所有主机的性能指标
                let current_metrics = Self::collect_metrics(&hosts).await;
                
                // 存储指标历史
                {
                    let mut history = metrics_history.lock().unwrap();
                    history.extend(current_metrics);
                    
                    // 保持历史记录大小限制
                    if history.len() > 1000 {
                        history.drain(0..history.len() - 1000);
                    }
                }
            }
        });

        Ok(())
    }

    /// 停止监控
    pub fn stop_monitoring(&self) {
        self.is_monitoring.store(false, Ordering::Relaxed);
    }

    /// 收集性能指标
    async fn collect_metrics(hosts: &Arc<Mutex<HashMap<String, ESXiHost>>>) -> Vec<VirtualizationMetrics> {
        let hosts_guard = hosts.lock().unwrap();
        let mut metrics = Vec::new();

        for (host_id, host) in hosts_guard.iter() {
            let metric = VirtualizationMetrics {
                host_id: host_id.clone(),
                timestamp: SystemTime::now().duration_since(UNIX_EPOCH)
                    .unwrap().as_secs(),
                cpu_usage: Self::calculate_cpu_usage(host),
                memory_usage: Self::calculate_memory_usage(host),
                storage_io: Self::calculate_storage_metrics(host),
                network_io: Self::calculate_network_metrics(host),
                vm_count: host.virtual_machines.len() as u32,
                active_vm_count: host.virtual_machines.iter()
                    .filter(|vm| matches!(vm.status, VMStatus::Running))
                    .count() as u32,
                resource_allocation: Self::calculate_resource_allocation(host),
            };
            metrics.push(metric);
        }

        metrics
    }

    /// 计算CPU使用率
    fn calculate_cpu_usage(host: &ESXiHost) -> f64 {
        let total_cpu_usage: f64 = host.virtual_machines.iter()
            .map(|vm| vm.cpu_usage)
            .sum();
        
        // 模拟主机CPU使用率计算
        let host_overhead = 5.0; // 5%的主机开销
        (total_cpu_usage + host_overhead).min(100.0)
    }

    /// 计算内存使用率
    fn calculate_memory_usage(host: &ESXiHost) -> f64 {
        let total_memory_usage: f64 = host.virtual_machines.iter()
            .map(|vm| vm.memory_usage)
            .sum();
        
        // 模拟主机内存使用率计算
        let host_overhead = 2.0; // 2%的主机开销
        (total_memory_usage + host_overhead).min(100.0)
    }

    /// 计算存储指标
    fn calculate_storage_metrics(host: &ESXiHost) -> StorageMetrics {
        // 模拟存储性能数据
        StorageMetrics {
            read_iops: 1000 + (host.virtual_machines.len() as u64 * 50),
            write_iops: 800 + (host.virtual_machines.len() as u64 * 30),
            read_latency: 2.5 + (host.virtual_machines.len() as f64 * 0.1),
            write_latency: 3.0 + (host.virtual_machines.len() as f64 * 0.15),
            usage_percentage: host.virtual_machines.iter()
                .map(|vm| vm.storage_used)
                .sum::<f64>() / host.total_storage_gb as f64 * 100.0,
        }
    }

    /// 计算网络指标
    fn calculate_network_metrics(host: &ESXiHost) -> NetworkMetrics {
        // 模拟网络性能数据
        NetworkMetrics {
            inbound_bandwidth: 100.0 + (host.virtual_machines.len() as f64 * 10.0),
            outbound_bandwidth: 80.0 + (host.virtual_machines.len() as f64 * 8.0),
            inbound_packets: 10000 + (host.virtual_machines.len() as u64 * 1000),
            outbound_packets: 8000 + (host.virtual_machines.len() as u64 * 800),
            latency: 1.0 + (host.virtual_machines.len() as f64 * 0.05),
        }
    }

    /// 计算资源分配率
    fn calculate_resource_allocation(host: &ESXiHost) -> ResourceAllocation {
        ResourceAllocation {
            cpu_allocation: Self::calculate_cpu_usage(host),
            memory_allocation: Self::calculate_memory_usage(host),
            storage_allocation: host.virtual_machines.iter()
                .map(|vm| vm.storage_used)
                .sum::<f64>() / host.total_storage_gb as f64 * 100.0,
            network_allocation: host.virtual_machines.iter()
                .map(|vm| vm.network_used)
                .sum::<f64>() / 1000.0, // 假设1GB网络容量
        }
    }

    /// 获取性能指标历史
    pub fn get_metrics_history(&self, host_id: Option<&str>, limit: Option<usize>) -> Vec<VirtualizationMetrics> {
        let history = self.metrics_history.lock().unwrap();
        let mut filtered_history = if let Some(host_id) = host_id {
            history.iter()
                .filter(|metric| metric.host_id == host_id)
                .cloned()
                .collect()
        } else {
            history.clone()
        };

        if let Some(limit) = limit {
            filtered_history.truncate(limit);
        }

        filtered_history
    }

    /// 获取主机列表
    pub fn get_hosts(&self) -> Vec<ESXiHost> {
        let hosts = self.hosts.lock().unwrap();
        hosts.values().cloned().collect()
    }

    /// 获取特定主机的虚拟机列表
    pub fn get_virtual_machines(&self, host_id: &str) -> Result<Vec<VirtualMachine>> {
        let hosts = self.hosts.lock().unwrap();
        let host = hosts.get(host_id)
            .ok_or_else(|| anyhow::anyhow!("主机不存在: {}", host_id))?;
        Ok(host.virtual_machines.clone())
    }

    /// 生成性能报告
    pub fn generate_performance_report(&self, host_id: &str, duration_hours: u64) -> Result<PerformanceReport> {
        let history = self.get_metrics_history(Some(host_id), None);
        let cutoff_time = SystemTime::now().duration_since(UNIX_EPOCH)
            .unwrap().as_secs() - (duration_hours * 3600);
        
        let recent_metrics: Vec<_> = history.into_iter()
            .filter(|metric| metric.timestamp >= cutoff_time)
            .collect();

        if recent_metrics.is_empty() {
            return Err(anyhow::anyhow!("没有找到指定时间范围内的数据"));
        }

        let avg_cpu = recent_metrics.iter().map(|m| m.cpu_usage).sum::<f64>() / recent_metrics.len() as f64;
        let avg_memory = recent_metrics.iter().map(|m| m.memory_usage).sum::<f64>() / recent_metrics.len() as f64;
        let max_cpu = recent_metrics.iter().map(|m| m.cpu_usage).fold(0.0, f64::max);
        let max_memory = recent_metrics.iter().map(|m| m.memory_usage).fold(0.0, f64::max);

        Ok(PerformanceReport {
            host_id: host_id.to_string(),
            duration_hours,
            sample_count: recent_metrics.len(),
            average_cpu_usage: avg_cpu,
            average_memory_usage: avg_memory,
            peak_cpu_usage: max_cpu,
            peak_memory_usage: max_memory,
            average_vm_count: recent_metrics.iter().map(|m| m.vm_count).sum::<u32>() as f64 / recent_metrics.len() as f64,
            generated_at: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        })
    }
}

/// 性能报告
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceReport {
    /// 主机ID
    pub host_id: String,
    /// 报告时长(小时)
    pub duration_hours: u64,
    /// 样本数量
    pub sample_count: usize,
    /// 平均CPU使用率
    pub average_cpu_usage: f64,
    /// 平均内存使用率
    pub average_memory_usage: f64,
    /// 峰值CPU使用率
    pub peak_cpu_usage: f64,
    /// 峰值内存使用率
    pub peak_memory_usage: f64,
    /// 平均虚拟机数量
    pub average_vm_count: f64,
    /// 报告生成时间
    pub generated_at: u64,
}

/// 虚拟化资源调度器
pub struct VirtualizationScheduler {
    /// 监控器引用
    monitor: Arc<VirtualizationMonitor>,
    /// 调度策略
    strategy: SchedulingStrategy,
    /// 负载均衡阈值
    load_balance_threshold: f64,
}

/// 调度策略
#[derive(Debug, Clone)]
pub enum SchedulingStrategy {
    /// 轮询调度
    RoundRobin,
    /// 最少连接调度
    LeastConnections,
    /// 加权轮询调度
    WeightedRoundRobin,
    /// 基于负载的调度
    LoadBased,
}

impl VirtualizationScheduler {
    /// 创建新的调度器
    pub fn new(monitor: Arc<VirtualizationMonitor>, strategy: SchedulingStrategy) -> Self {
        Self {
            monitor,
            strategy,
            load_balance_threshold: 80.0,
        }
    }

    /// 选择最佳主机部署虚拟机
    pub fn select_host_for_vm(&self, vm_requirements: &VMRequirements) -> Result<String> {
        let hosts = self.monitor.get_hosts();
        
        if hosts.is_empty() {
            return Err(anyhow::anyhow!("没有可用的主机"));
        }

        let selected_host = match self.strategy {
            SchedulingStrategy::RoundRobin => {
                self.select_by_round_robin(&hosts)
            }
            SchedulingStrategy::LeastConnections => {
                self.select_by_least_connections(&hosts)
            }
            SchedulingStrategy::WeightedRoundRobin => {
                self.select_by_weighted_round_robin(&hosts)
            }
            SchedulingStrategy::LoadBased => {
                self.select_by_load(&hosts, vm_requirements)
            }
        };

        Ok(selected_host)
    }

    /// 轮询调度
    fn select_by_round_robin(&self, hosts: &[ESXiHost]) -> String {
        // 简化实现，实际应该维护状态
        hosts[0].host_id.clone()
    }

    /// 最少连接调度
    fn select_by_least_connections(&self, hosts: &[ESXiHost]) -> String {
        hosts.iter()
            .min_by_key(|host| host.virtual_machines.len())
            .unwrap()
            .host_id.clone()
    }

    /// 加权轮询调度
    fn select_by_weighted_round_robin(&self, hosts: &[ESXiHost]) -> String {
        // 基于主机资源容量进行加权
        let mut best_host = &hosts[0];
        let mut best_score = 0.0;

        for host in hosts {
            let score = (host.total_cpu_cores as f64 * 0.4) + 
                       (host.total_memory_gb as f64 * 0.3) + 
                       (host.total_storage_gb as f64 * 0.3);
            
            if score > best_score {
                best_score = score;
                best_host = host;
            }
        }

        best_host.host_id.clone()
    }

    /// 基于负载的调度
    fn select_by_load(&self, hosts: &[ESXiHost], vm_requirements: &VMRequirements) -> String {
        let mut best_host = None;
        let mut best_load = f64::MAX;

        for host in hosts {
            let current_load = self.calculate_host_load(host);
            let projected_load = current_load + self.calculate_vm_load(vm_requirements);
            
            if projected_load < best_load && projected_load <= self.load_balance_threshold {
                best_load = projected_load;
                best_host = Some(host);
            }
        }

        best_host.unwrap_or(&hosts[0]).host_id.clone()
    }

    /// 计算主机负载
    fn calculate_host_load(&self, host: &ESXiHost) -> f64 {
        let cpu_load = host.virtual_machines.iter()
            .map(|vm| vm.cpu_usage)
            .sum::<f64>() / host.total_cpu_cores as f64;
        
        let memory_load = host.virtual_machines.iter()
            .map(|vm| vm.memory_usage)
            .sum::<f64>() / 100.0; // 假设100%为满负载

        (cpu_load + memory_load) / 2.0
    }

    /// 计算虚拟机负载
    fn calculate_vm_load(&self, vm_requirements: &VMRequirements) -> f64 {
        (vm_requirements.cpu_cores as f64 * 0.5) + (vm_requirements.memory_gb as f64 * 0.5)
    }

    /// 执行负载均衡
    pub async fn perform_load_balancing(&self) -> Result<Vec<MigrationPlan>> {
        let hosts = self.monitor.get_hosts();
        let mut migration_plans = Vec::new();

        // 识别过载主机
        let overloaded_hosts: Vec<_> = hosts.iter()
            .filter(|host| self.calculate_host_load(host) > self.load_balance_threshold)
            .collect();

        // 识别轻载主机
        let underloaded_hosts: Vec<_> = hosts.iter()
            .filter(|host| self.calculate_host_load(host) < (self.load_balance_threshold * 0.5))
            .collect();

        // 生成迁移计划
        for overloaded_host in overloaded_hosts {
            if let Some(target_host) = underloaded_hosts.first() {
                let migration_plan = self.create_migration_plan(overloaded_host, target_host)?;
                migration_plans.push(migration_plan);
            }
        }

        Ok(migration_plans)
    }

    /// 创建迁移计划
    fn create_migration_plan(&self, source_host: &ESXiHost, target_host: &ESXiHost) -> Result<MigrationPlan> {
        // 选择要迁移的虚拟机（选择负载较低的）
        let vm_to_migrate = source_host.virtual_machines.iter()
            .filter(|vm| matches!(vm.status, VMStatus::Running))
            .min_by(|a, b| a.cpu_usage.partial_cmp(&b.cpu_usage).unwrap())
            .ok_or_else(|| anyhow::anyhow!("没有可迁移的虚拟机"))?;

        Ok(MigrationPlan {
            vm_id: vm_to_migrate.vm_id.clone(),
            source_host_id: source_host.host_id.clone(),
            target_host_id: target_host.host_id.clone(),
            estimated_downtime: Duration::from_secs(30), // 估算停机时间
            migration_priority: MigrationPriority::Normal,
        })
    }
}

/// 虚拟机需求
#[derive(Debug, Clone)]
pub struct VMRequirements {
    /// CPU核心数
    pub cpu_cores: u32,
    /// 内存大小(GB)
    pub memory_gb: u64,
    /// 存储大小(GB)
    pub storage_gb: u64,
    /// 网络带宽(Mbps)
    pub network_mbps: u64,
}

/// 迁移计划
#[derive(Debug, Clone)]
pub struct MigrationPlan {
    /// 虚拟机ID
    pub vm_id: String,
    /// 源主机ID
    pub source_host_id: String,
    /// 目标主机ID
    pub target_host_id: String,
    /// 估算停机时间
    pub estimated_downtime: Duration,
    /// 迁移优先级
    pub migration_priority: MigrationPriority,
}

/// 迁移优先级
#[derive(Debug, Clone)]
pub enum MigrationPriority {
    Low,
    Normal,
    High,
    Critical,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_virtualization_monitor_creation() {
        let monitor = VirtualizationMonitor::new(60, 1000);
        assert_eq!(monitor.monitoring_interval, 60);
        assert_eq!(monitor.max_history_size, 1000);
    }

    #[test]
    fn test_host_management() {
        let monitor = VirtualizationMonitor::new(60, 1000);
        
        let host = ESXiHost {
            host_id: "host-001".to_string(),
            name: "ESXi-01".to_string(),
            ip_address: "192.168.1.100".to_string(),
            total_cpu_cores: 16,
            total_memory_gb: 128,
            total_storage_gb: 2000,
            virtual_machines: vec![],
            last_updated: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        };

        monitor.add_host(host.clone()).unwrap();
        let hosts = monitor.get_hosts();
        assert_eq!(hosts.len(), 1);
        assert_eq!(hosts[0].host_id, "host-001");

        monitor.remove_host("host-001").unwrap();
        let hosts = monitor.get_hosts();
        assert_eq!(hosts.len(), 0);
    }

    #[test]
    fn test_metrics_calculation() {
        let host = ESXiHost {
            host_id: "host-001".to_string(),
            name: "ESXi-01".to_string(),
            ip_address: "192.168.1.100".to_string(),
            total_cpu_cores: 16,
            total_memory_gb: 128,
            total_storage_gb: 2000,
            virtual_machines: vec![
                VirtualMachine {
                    vm_id: "vm-001".to_string(),
                    name: "VM-01".to_string(),
                    status: VMStatus::Running,
                    cpu_usage: 25.0,
                    memory_usage: 30.0,
                    storage_used: 100.0,
                    network_used: 50.0,
                    uptime: 3600,
                }
            ],
            last_updated: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        };

        let cpu_usage = VirtualizationMonitor::calculate_cpu_usage(&host);
        assert!(cpu_usage > 0.0);
        assert!(cpu_usage <= 100.0);

        let memory_usage = VirtualizationMonitor::calculate_memory_usage(&host);
        assert!(memory_usage > 0.0);
        assert!(memory_usage <= 100.0);
    }

    #[tokio::test]
    async fn test_scheduler_selection() {
        let monitor = Arc::new(VirtualizationMonitor::new(60, 1000));
        
        let host1 = ESXiHost {
            host_id: "host-001".to_string(),
            name: "ESXi-01".to_string(),
            ip_address: "192.168.1.100".to_string(),
            total_cpu_cores: 16,
            total_memory_gb: 128,
            total_storage_gb: 2000,
            virtual_machines: vec![],
            last_updated: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        };

        let host2 = ESXiHost {
            host_id: "host-002".to_string(),
            name: "ESXi-02".to_string(),
            ip_address: "192.168.1.101".to_string(),
            total_cpu_cores: 32,
            total_memory_gb: 256,
            total_storage_gb: 4000,
            virtual_machines: vec![],
            last_updated: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
        };

        monitor.add_host(host1).unwrap();
        monitor.add_host(host2).unwrap();

        let scheduler = VirtualizationScheduler::new(
            monitor,
            SchedulingStrategy::LeastConnections
        );

        let vm_requirements = VMRequirements {
            cpu_cores: 4,
            memory_gb: 8,
            storage_gb: 100,
            network_mbps: 100,
        };

        let selected_host = scheduler.select_host_for_vm(&vm_requirements).unwrap();
        assert!(!selected_host.is_empty());
    }
}

/// 主函数示例
#[tokio::main]
async fn main() -> Result<()> {
    println!("虚拟化性能监控器启动...");

    // 创建监控器
    let monitor = Arc::new(VirtualizationMonitor::new(30, 1000));

    // 添加示例主机
    let host1 = ESXiHost {
        host_id: "host-001".to_string(),
        name: "ESXi-01".to_string(),
        ip_address: "192.168.1.100".to_string(),
        total_cpu_cores: 16,
        total_memory_gb: 128,
        total_storage_gb: 2000,
        virtual_machines: vec![
            VirtualMachine {
                vm_id: "vm-001".to_string(),
                name: "Web-Server-01".to_string(),
                status: VMStatus::Running,
                cpu_usage: 25.0,
                memory_usage: 30.0,
                storage_used: 100.0,
                network_used: 50.0,
                uptime: 3600,
            },
            VirtualMachine {
                vm_id: "vm-002".to_string(),
                name: "DB-Server-01".to_string(),
                status: VMStatus::Running,
                cpu_usage: 45.0,
                memory_usage: 60.0,
                storage_used: 500.0,
                network_used: 20.0,
                uptime: 7200,
            },
        ],
        last_updated: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
    };

    monitor.add_host(host1)?;

    // 创建调度器
    let scheduler = VirtualizationScheduler::new(
        Arc::clone(&monitor),
        SchedulingStrategy::LoadBased
    );

    // 开始监控
    monitor.start_monitoring().await?;
    println!("监控已启动，每30秒收集一次指标");

    // 等待一段时间收集数据
    tokio::time::sleep(Duration::from_secs(60)).await;

    // 生成性能报告
    let report = monitor.generate_performance_report("host-001", 1)?;
    println!("性能报告:");
    println!("  平均CPU使用率: {:.2}%", report.average_cpu_usage);
    println!("  平均内存使用率: {:.2}%", report.average_memory_usage);
    println!("  峰值CPU使用率: {:.2}%", report.peak_cpu_usage);
    println!("  峰值内存使用率: {:.2}%", report.peak_memory_usage);

    // 测试调度器
    let vm_requirements = VMRequirements {
        cpu_cores: 4,
        memory_gb: 8,
        storage_gb: 100,
        network_mbps: 100,
    };

    let selected_host = scheduler.select_host_for_vm(&vm_requirements)?;
    println!("为虚拟机选择的主机: {}", selected_host);

    // 执行负载均衡
    let migration_plans = scheduler.perform_load_balancing().await?;
    if !migration_plans.is_empty() {
        println!("生成了 {} 个迁移计划", migration_plans.len());
        for plan in migration_plans {
            println!("  迁移虚拟机 {} 从 {} 到 {}", 
                plan.vm_id, plan.source_host_id, plan.target_host_id);
        }
    } else {
        println!("当前负载均衡，无需迁移");
    }

    // 停止监控
    monitor.stop_monitoring();
    println!("监控已停止");

    Ok(())
}
