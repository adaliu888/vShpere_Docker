//! 性能基准测试框架
//! 
//! 这是一个用Rust实现的性能基准测试框架，用于测试虚拟化和容器化技术的性能。
//! 该实现展示了性能测试的实际应用，包括CPU、内存、存储、网络等各方面的性能测试。

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use std::thread;
use std::sync::atomic::{AtomicU64, AtomicBool, Ordering};
use serde::{Deserialize, Serialize};
use anyhow::{Result, Context};

/// 性能基准测试框架
pub struct PerformanceBenchmark {
    test_suites: HashMap<String, TestSuite>,
    results: Arc<Mutex<Vec<BenchmarkResult>>>,
    is_running: AtomicBool,
}

/// 测试套件
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestSuite {
    pub name: String,
    pub description: String,
    pub tests: Vec<BenchmarkTest>,
    pub iterations: u32,
    pub warmup_iterations: u32,
    pub timeout: Duration,
}

/// 基准测试
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenchmarkTest {
    pub name: String,
    pub description: String,
    pub test_type: TestType,
    pub parameters: HashMap<String, String>,
    pub expected_result: Option<f64>,
    pub threshold: Option<f64>,
}

/// 测试类型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TestType {
    CpuIntensive,
    MemoryIntensive,
    StorageIO,
    NetworkIO,
    Concurrent,
    Virtualization,
    Containerization,
    MixedWorkload,
}

/// 基准测试结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenchmarkResult {
    pub test_suite: String,
    pub test_name: String,
    pub test_type: TestType,
    pub iterations: u32,
    pub total_duration: Duration,
    pub average_duration: Duration,
    pub min_duration: Duration,
    pub max_duration: Duration,
    pub throughput: f64,
    pub cpu_usage: f64,
    pub memory_usage: f64,
    pub success_rate: f64,
    pub error_count: u32,
    pub details: HashMap<String, String>,
    pub timestamp: String,
}

/// CPU密集型测试
pub struct CpuIntensiveTest {
    pub iterations: u64,
    pub complexity: u32,
}

/// 内存密集型测试
pub struct MemoryIntensiveTest {
    pub memory_size: usize,
    pub operations: u32,
    pub access_pattern: AccessPattern,
}

/// 存储IO测试
pub struct StorageIOTest {
    pub file_size: u64,
    pub block_size: usize,
    pub operation_type: IOOperation,
    pub concurrent_ops: u32,
}

/// 网络IO测试
pub struct NetworkIOTest {
    pub data_size: usize,
    pub connections: u32,
    pub protocol: NetworkProtocol,
    pub latency_test: bool,
}

/// 访问模式
#[derive(Debug, Clone)]
pub enum AccessPattern {
    Sequential,
    Random,
    Stride,
}

/// IO操作类型
#[derive(Debug, Clone)]
pub enum IOOperation {
    Read,
    Write,
    ReadWrite,
    RandomRead,
    RandomWrite,
}

/// 网络协议
#[derive(Debug, Clone)]
pub enum NetworkProtocol {
    TCP,
    UDP,
    HTTP,
    HTTPS,
}

impl PerformanceBenchmark {
    /// 创建新的性能基准测试框架
    pub fn new() -> Self {
        Self {
            test_suites: HashMap::new(),
            results: Arc::new(Mutex::new(Vec::new())),
            is_running: AtomicBool::new(false),
        }
    }

    /// 添加测试套件
    pub fn add_test_suite(&mut self, suite: TestSuite) {
        self.test_suites.insert(suite.name.clone(), suite);
    }

    /// 运行所有测试套件
    pub async fn run_all_tests(&self) -> Result<Vec<BenchmarkResult>> {
        if self.is_running.load(Ordering::Relaxed) {
            return Err(anyhow::anyhow!("测试已在运行"));
        }

        self.is_running.store(true, Ordering::Relaxed);
        let mut all_results = Vec::new();

        for (suite_name, suite) in &self.test_suites {
            println!("运行测试套件: {}", suite_name);
            let results = self.run_test_suite(suite).await?;
            all_results.extend(results);
        }

        self.is_running.store(false, Ordering::Relaxed);
        Ok(all_results)
    }

    /// 运行单个测试套件
    async fn run_test_suite(&self, suite: &TestSuite) -> Result<Vec<BenchmarkResult>> {
        let mut results = Vec::new();

        for test in &suite.tests {
            println!("  运行测试: {}", test.name);
            let result = self.run_single_test(suite, test).await?;
            results.push(result);
        }

        Ok(results)
    }

    /// 运行单个测试
    async fn run_single_test(&self, suite: &TestSuite, test: &BenchmarkTest) -> Result<BenchmarkResult> {
        let start_time = Instant::now();
        let mut durations = Vec::new();
        let mut error_count = 0u32;
        let mut success_count = 0u32;

        // 预热
        for _ in 0..suite.warmup_iterations {
            if let Err(_) = self.execute_test(test).await {
                // 忽略预热错误
            }
        }

        // 正式测试
        for iteration in 0..suite.iterations {
            let test_start = Instant::now();
            
            match self.execute_test(test).await {
                Ok(_) => {
                    success_count += 1;
                    durations.push(test_start.elapsed());
                }
                Err(_) => {
                    error_count += 1;
                }
            }

            // 检查超时
            if start_time.elapsed() > suite.timeout {
                break;
            }
        }

        let total_duration = start_time.elapsed();
        let iterations = durations.len() as u32;

        // 计算统计信息
        let average_duration = if !durations.is_empty() {
            durations.iter().sum::<Duration>() / durations.len() as u32
        } else {
            Duration::from_secs(0)
        };

        let min_duration = durations.iter().min().copied().unwrap_or(Duration::from_secs(0));
        let max_duration = durations.iter().max().copied().unwrap_or(Duration::from_secs(0));

        let throughput = if average_duration.as_nanos() > 0 {
            1_000_000_000.0 / average_duration.as_nanos() as f64
        } else {
            0.0
        };

        let success_rate = if iterations > 0 {
            success_count as f64 / iterations as f64 * 100.0
        } else {
            0.0
        };

        // 获取系统资源使用情况
        let (cpu_usage, memory_usage) = self.get_system_metrics().await?;

        let result = BenchmarkResult {
            test_suite: suite.name.clone(),
            test_name: test.name.clone(),
            test_type: test.test_type.clone(),
            iterations,
            total_duration,
            average_duration,
            min_duration,
            max_duration,
            throughput,
            cpu_usage,
            memory_usage,
            success_rate,
            error_count,
            details: test.parameters.clone(),
            timestamp: chrono::Utc::now().to_rfc3339(),
        };

        // 存储结果
        {
            let mut results = self.results.lock().unwrap();
            results.push(result.clone());
        }

        Ok(result)
    }

    /// 执行单个测试
    async fn execute_test(&self, test: &BenchmarkTest) -> Result<()> {
        match test.test_type {
            TestType::CpuIntensive => {
                self.run_cpu_test(test).await
            }
            TestType::MemoryIntensive => {
                self.run_memory_test(test).await
            }
            TestType::StorageIO => {
                self.run_storage_test(test).await
            }
            TestType::NetworkIO => {
                self.run_network_test(test).await
            }
            TestType::Concurrent => {
                self.run_concurrent_test(test).await
            }
            TestType::Virtualization => {
                self.run_virtualization_test(test).await
            }
            TestType::Containerization => {
                self.run_containerization_test(test).await
            }
            TestType::MixedWorkload => {
                self.run_mixed_workload_test(test).await
            }
        }
    }

    /// 运行CPU测试
    async fn run_cpu_test(&self, test: &BenchmarkTest) -> Result<()> {
        let iterations: u64 = test.parameters.get("iterations")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1_000_000);
        
        let complexity: u32 = test.parameters.get("complexity")
            .and_then(|s| s.parse().ok())
            .unwrap_or(10);

        // CPU密集型计算
        let mut result = 0u64;
        for i in 0..iterations {
            result = result.wrapping_add(i * complexity as u64);
            result = result.wrapping_mul(3);
            result = result.wrapping_add(1);
        }

        // 防止编译器优化
        std::hint::black_box(result);
        Ok(())
    }

    /// 运行内存测试
    async fn run_memory_test(&self, test: &BenchmarkTest) -> Result<()> {
        let memory_size: usize = test.parameters.get("memory_size")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1024 * 1024); // 1MB
        
        let operations: u32 = test.parameters.get("operations")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1000);

        // 分配内存
        let mut data = vec![0u8; memory_size];
        
        // 执行内存操作
        for _ in 0..operations {
            for i in 0..memory_size {
                data[i] = data[i].wrapping_add(1);
            }
        }

        // 防止编译器优化
        std::hint::black_box(data);
        Ok(())
    }

    /// 运行存储测试
    async fn run_storage_test(&self, test: &BenchmarkTest) -> Result<()> {
        let file_size: u64 = test.parameters.get("file_size")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1024 * 1024); // 1MB
        
        let block_size: usize = test.parameters.get("block_size")
            .and_then(|s| s.parse().ok())
            .unwrap_or(4096);

        // 创建临时文件
        let temp_file = std::env::temp_dir().join("benchmark_test.tmp");
        
        // 写入测试
        let data = vec![0u8; block_size];
        let mut file = std::fs::File::create(&temp_file)?;
        
        for _ in 0..(file_size / block_size as u64) {
            use std::io::Write;
            file.write_all(&data)?;
        }
        file.sync_all()?;
        drop(file);

        // 读取测试
        let mut file = std::fs::File::open(&temp_file)?;
        let mut buffer = vec![0u8; block_size];
        
        for _ in 0..(file_size / block_size as u64) {
            use std::io::Read;
            file.read_exact(&mut buffer)?;
        }

        // 清理临时文件
        let _ = std::fs::remove_file(&temp_file);
        Ok(())
    }

    /// 运行网络测试
    async fn run_network_test(&self, test: &BenchmarkTest) -> Result<()> {
        let data_size: usize = test.parameters.get("data_size")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1024);
        
        let connections: u32 = test.parameters.get("connections")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1);

        // 模拟网络操作
        let data = vec![0u8; data_size];
        
        for _ in 0..connections {
            // 模拟网络延迟
            tokio::time::sleep(Duration::from_millis(1)).await;
            
            // 模拟数据处理
            let _processed_data: Vec<u8> = data.iter()
                .map(|&b| b.wrapping_add(1))
                .collect();
        }

        Ok(())
    }

    /// 运行并发测试
    async fn run_concurrent_test(&self, test: &BenchmarkTest) -> Result<()> {
        let threads: u32 = test.parameters.get("threads")
            .and_then(|s| s.parse().ok())
            .unwrap_or(4);
        
        let work_per_thread: u32 = test.parameters.get("work_per_thread")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1000);

        let handles: Vec<_> = (0..threads)
            .map(|_| {
                let work = work_per_thread;
                thread::spawn(move || {
                    let mut result = 0u64;
                    for i in 0..work {
                        result = result.wrapping_add(i as u64);
                    }
                    result
                })
            })
            .collect();

        let mut total_result = 0u64;
        for handle in handles {
            total_result = total_result.wrapping_add(handle.join().unwrap());
        }

        std::hint::black_box(total_result);
        Ok(())
    }

    /// 运行虚拟化测试
    async fn run_virtualization_test(&self, test: &BenchmarkTest) -> Result<()> {
        let vm_count: u32 = test.parameters.get("vm_count")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1);
        
        let operations_per_vm: u32 = test.parameters.get("operations_per_vm")
            .and_then(|s| s.parse().ok())
            .unwrap_or(100);

        // 模拟虚拟机操作
        for vm_id in 0..vm_count {
            for _ in 0..operations_per_vm {
                // 模拟虚拟机上下文切换开销
                tokio::time::sleep(Duration::from_micros(10)).await;
                
                // 模拟虚拟机内部计算
                let mut result = 0u64;
                for i in 0..1000 {
                    result = result.wrapping_add(i * vm_id as u64);
                }
                std::hint::black_box(result);
            }
        }

        Ok(())
    }

    /// 运行容器化测试
    async fn run_containerization_test(&self, test: &BenchmarkTest) -> Result<()> {
        let container_count: u32 = test.parameters.get("container_count")
            .and_then(|s| s.parse().ok())
            .unwrap_or(1);
        
        let operations_per_container: u32 = test.parameters.get("operations_per_container")
            .and_then(|s| s.parse().ok())
            .unwrap_or(100);

        // 模拟容器操作
        for container_id in 0..container_count {
            for _ in 0..operations_per_container {
                // 模拟容器启动开销
                tokio::time::sleep(Duration::from_micros(5)).await;
                
                // 模拟容器内应用执行
                let mut result = 0u64;
                for i in 0..500 {
                    result = result.wrapping_add(i * container_id as u64);
                }
                std::hint::black_box(result);
            }
        }

        Ok(())
    }

    /// 运行混合工作负载测试
    async fn run_mixed_workload_test(&self, test: &BenchmarkTest) -> Result<()> {
        let workload_ratio: f64 = test.parameters.get("workload_ratio")
            .and_then(|s| s.parse().ok())
            .unwrap_or(0.5);

        // 混合CPU和IO操作
        let cpu_operations = (1000.0 * workload_ratio) as u32;
        let io_operations = (1000.0 * (1.0 - workload_ratio)) as u32;

        // CPU操作
        for _ in 0..cpu_operations {
            let mut result = 0u64;
            for i in 0..100 {
                result = result.wrapping_add(i);
            }
            std::hint::black_box(result);
        }

        // IO操作
        for _ in 0..io_operations {
            tokio::time::sleep(Duration::from_micros(100)).await;
        }

        Ok(())
    }

    /// 获取系统指标
    async fn get_system_metrics(&self) -> Result<(f64, f64)> {
        // 模拟获取系统指标
        let cpu_usage = 45.0 + (rand::random::<f64>() * 20.0); // 45-65%
        let memory_usage = 60.0 + (rand::random::<f64>() * 15.0); // 60-75%
        
        Ok((cpu_usage, memory_usage))
    }

    /// 获取测试结果
    pub fn get_results(&self) -> Vec<BenchmarkResult> {
        let results = self.results.lock().unwrap();
        results.clone()
    }

    /// 生成性能报告
    pub fn generate_performance_report(&self) -> Result<PerformanceReport> {
        let results = self.get_results();
        
        if results.is_empty() {
            return Err(anyhow::anyhow!("没有测试结果"));
        }

        let total_tests = results.len();
        let total_duration: Duration = results.iter().map(|r| r.total_duration).sum();
        let average_throughput = results.iter().map(|r| r.throughput).sum::<f64>() / total_tests as f64;
        let average_success_rate = results.iter().map(|r| r.success_rate).sum::<f64>() / total_tests as f64;

        // 按测试类型分组
        let mut type_stats: HashMap<String, Vec<&BenchmarkResult>> = HashMap::new();
        for result in &results {
            let type_name = format!("{:?}", result.test_type);
            type_stats.entry(type_name).or_insert_with(Vec::new).push(result);
        }

        Ok(PerformanceReport {
            total_tests,
            total_duration,
            average_throughput,
            average_success_rate,
            type_statistics: type_stats.into_iter()
                .map(|(k, v)| (k, TypeStatistics {
                    count: v.len(),
                    average_throughput: v.iter().map(|r| r.throughput).sum::<f64>() / v.len() as f64,
                    average_success_rate: v.iter().map(|r| r.success_rate).sum::<f64>() / v.len() as f64,
                }))
                .collect(),
            results,
            generated_at: chrono::Utc::now().to_rfc3339(),
        })
    }
}

/// 性能报告
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceReport {
    pub total_tests: usize,
    pub total_duration: Duration,
    pub average_throughput: f64,
    pub average_success_rate: f64,
    pub type_statistics: HashMap<String, TypeStatistics>,
    pub results: Vec<BenchmarkResult>,
    pub generated_at: String,
}

/// 类型统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TypeStatistics {
    pub count: usize,
    pub average_throughput: f64,
    pub average_success_rate: f64,
}

/// 创建默认测试套件
pub fn create_default_test_suites() -> Vec<TestSuite> {
    vec![
        TestSuite {
            name: "CPU性能测试".to_string(),
            description: "测试CPU密集型操作性能".to_string(),
            iterations: 10,
            warmup_iterations: 2,
            timeout: Duration::from_secs(30),
            tests: vec![
                BenchmarkTest {
                    name: "CPU计算测试".to_string(),
                    description: "测试CPU计算性能".to_string(),
                    test_type: TestType::CpuIntensive,
                    parameters: {
                        let mut params = HashMap::new();
                        params.insert("iterations".to_string(), "1000000".to_string());
                        params.insert("complexity".to_string(), "10".to_string());
                        params
                    },
                    expected_result: Some(1000000.0),
                    threshold: Some(0.8),
                },
            ],
        },
        TestSuite {
            name: "内存性能测试".to_string(),
            description: "测试内存操作性能".to_string(),
            iterations: 5,
            warmup_iterations: 1,
            timeout: Duration::from_secs(20),
            tests: vec![
                BenchmarkTest {
                    name: "内存访问测试".to_string(),
                    description: "测试内存访问性能".to_string(),
                    test_type: TestType::MemoryIntensive,
                    parameters: {
                        let mut params = HashMap::new();
                        params.insert("memory_size".to_string(), "1048576".to_string()); // 1MB
                        params.insert("operations".to_string(), "1000".to_string());
                        params
                    },
                    expected_result: Some(1000.0),
                    threshold: Some(0.9),
                },
            ],
        },
        TestSuite {
            name: "存储IO测试".to_string(),
            description: "测试存储IO性能".to_string(),
            iterations: 3,
            warmup_iterations: 1,
            timeout: Duration::from_secs(60),
            tests: vec![
                BenchmarkTest {
                    name: "文件读写测试".to_string(),
                    description: "测试文件读写性能".to_string(),
                    test_type: TestType::StorageIO,
                    parameters: {
                        let mut params = HashMap::new();
                        params.insert("file_size".to_string(), "1048576".to_string()); // 1MB
                        params.insert("block_size".to_string(), "4096".to_string());
                        params
                    },
                    expected_result: Some(100.0),
                    threshold: Some(0.7),
                },
            ],
        },
        TestSuite {
            name: "并发性能测试".to_string(),
            description: "测试并发操作性能".to_string(),
            iterations: 5,
            warmup_iterations: 1,
            timeout: Duration::from_secs(30),
            tests: vec![
                BenchmarkTest {
                    name: "多线程测试".to_string(),
                    description: "测试多线程性能".to_string(),
                    test_type: TestType::Concurrent,
                    parameters: {
                        let mut params = HashMap::new();
                        params.insert("threads".to_string(), "4".to_string());
                        params.insert("work_per_thread".to_string(), "10000".to_string());
                        params
                    },
                    expected_result: Some(40000.0),
                    threshold: Some(0.8),
                },
            ],
        },
        TestSuite {
            name: "虚拟化性能测试".to_string(),
            description: "测试虚拟化性能开销".to_string(),
            iterations: 3,
            warmup_iterations: 1,
            timeout: Duration::from_secs(45),
            tests: vec![
                BenchmarkTest {
                    name: "虚拟机开销测试".to_string(),
                    description: "测试虚拟机性能开销".to_string(),
                    test_type: TestType::Virtualization,
                    parameters: {
                        let mut params = HashMap::new();
                        params.insert("vm_count".to_string(), "2".to_string());
                        params.insert("operations_per_vm".to_string(), "1000".to_string());
                        params
                    },
                    expected_result: Some(2000.0),
                    threshold: Some(0.6),
                },
            ],
        },
        TestSuite {
            name: "容器化性能测试".to_string(),
            description: "测试容器化性能开销".to_string(),
            iterations: 3,
            warmup_iterations: 1,
            timeout: Duration::from_secs(30),
            tests: vec![
                BenchmarkTest {
                    name: "容器开销测试".to_string(),
                    description: "测试容器性能开销".to_string(),
                    test_type: TestType::Containerization,
                    parameters: {
                        let mut params = HashMap::new();
                        params.insert("container_count".to_string(), "4".to_string());
                        params.insert("operations_per_container".to_string(), "500".to_string());
                        params
                    },
                    expected_result: Some(2000.0),
                    threshold: Some(0.8),
                },
            ],
        },
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_benchmark_framework() {
        let mut benchmark = PerformanceBenchmark::new();
        
        // 添加测试套件
        for suite in create_default_test_suites() {
            benchmark.add_test_suite(suite);
        }

        // 运行测试
        let results = benchmark.run_all_tests().await.unwrap();
        
        assert!(!results.is_empty());
        println!("测试结果数量: {}", results.len());
    }

    #[tokio::test]
    async fn test_cpu_benchmark() {
        let mut benchmark = PerformanceBenchmark::new();
        
        let suite = TestSuite {
            name: "CPU测试".to_string(),
            description: "测试CPU性能".to_string(),
            iterations: 3,
            warmup_iterations: 1,
            timeout: Duration::from_secs(10),
            tests: vec![
                BenchmarkTest {
                    name: "CPU计算".to_string(),
                    description: "CPU计算测试".to_string(),
                    test_type: TestType::CpuIntensive,
                    parameters: {
                        let mut params = HashMap::new();
                        params.insert("iterations".to_string(), "100000".to_string());
                        params.insert("complexity".to_string(), "5".to_string());
                        params
                    },
                    expected_result: None,
                    threshold: None,
                },
            ],
        };

        benchmark.add_test_suite(suite);
        let results = benchmark.run_all_tests().await.unwrap();
        
        assert_eq!(results.len(), 1);
        assert!(results[0].throughput > 0.0);
    }

    #[test]
    fn test_performance_report_generation() {
        let benchmark = PerformanceBenchmark::new();
        
        // 创建模拟结果
        let result = BenchmarkResult {
            test_suite: "测试套件".to_string(),
            test_name: "测试".to_string(),
            test_type: TestType::CpuIntensive,
            iterations: 10,
            total_duration: Duration::from_secs(1),
            average_duration: Duration::from_millis(100),
            min_duration: Duration::from_millis(90),
            max_duration: Duration::from_millis(110),
            throughput: 10.0,
            cpu_usage: 50.0,
            memory_usage: 60.0,
            success_rate: 100.0,
            error_count: 0,
            details: HashMap::new(),
            timestamp: chrono::Utc::now().to_rfc3339(),
        };

        {
            let mut results = benchmark.results.lock().unwrap();
            results.push(result);
        }

        let report = benchmark.generate_performance_report().unwrap();
        assert_eq!(report.total_tests, 1);
        assert_eq!(report.average_throughput, 10.0);
    }
}

/// 主函数示例
#[tokio::main]
async fn main() -> Result<()> {
    println!("性能基准测试框架启动...");

    // 创建基准测试框架
    let mut benchmark = PerformanceBenchmark::new();

    // 添加默认测试套件
    for suite in create_default_test_suites() {
        benchmark.add_test_suite(suite);
    }

    println!("开始运行性能基准测试...");
    
    // 运行所有测试
    let results = benchmark.run_all_tests().await?;

    println!("性能基准测试完成！");
    println!("总测试数: {}", results.len());

    // 生成性能报告
    let report = benchmark.generate_performance_report()?;

    println!("\n=== 性能报告 ===");
    println!("总测试数: {}", report.total_tests);
    println!("总耗时: {:?}", report.total_duration);
    println!("平均吞吐量: {:.2} ops/sec", report.average_throughput);
    println!("平均成功率: {:.1}%", report.average_success_rate);

    println!("\n=== 按类型统计 ===");
    for (type_name, stats) in &report.type_statistics {
        println!("{}: {} 个测试, 平均吞吐量: {:.2} ops/sec, 成功率: {:.1}%",
            type_name, stats.count, stats.average_throughput, stats.average_success_rate);
    }

    println!("\n=== 详细结果 ===");
    for result in &results {
        println!("{} - {}: {:.2} ops/sec, 成功率: {:.1}%, 耗时: {:?}",
            result.test_suite, result.test_name, 
            result.throughput, result.success_rate, result.average_duration);
    }

    // 保存结果到文件
    let report_json = serde_json::to_string_pretty(&report)?;
    std::fs::write("performance_report.json", report_json)?;
    println!("\n性能报告已保存到 performance_report.json");

    println!("\n性能基准测试框架运行完成");
    Ok(())
}
