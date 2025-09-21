// Package orchestrator 实现了一个容器编排器，用于管理Docker容器的生命周期、调度和负载均衡。
// 该实现展示了容器化技术的实际应用，包括容器编排、服务发现、健康检查和自动扩缩容。

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"sync"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/network"
	"github.com/docker/docker/client"
	"github.com/gorilla/mux"
)

// ContainerOrchestrator 容器编排器
type ContainerOrchestrator struct {
	dockerClient  *client.Client
	services      map[string]*Service
	nodes         map[string]*Node
	mu            sync.RWMutex
	healthChecker *HealthChecker
	loadBalancer  *LoadBalancer
	scheduler     *Scheduler
}

// Service 服务定义
type Service struct {
	ID          string            `json:"id"`
	Name        string            `json:"name"`
	Image       string            `json:"image"`
	Replicas    int               `json:"replicas"`
	Port        int               `json:"port"`
	Environment map[string]string `json:"environment"`
	Labels      map[string]string `json:"labels"`
	Containers  []*Container      `json:"containers"`
	HealthCheck *HealthCheck      `json:"health_check"`
	CreatedAt   time.Time         `json:"created_at"`
	UpdatedAt   time.Time         `json:"updated_at"`
}

// Container 容器信息
type Container struct {
	ID        string            `json:"id"`
	ServiceID string            `json:"service_id"`
	NodeID    string            `json:"node_id"`
	Name      string            `json:"name"`
	Image     string            `json:"image"`
	Status    ContainerStatus   `json:"status"`
	Port      int               `json:"port"`
	IP        string            `json:"ip"`
	CreatedAt time.Time         `json:"created_at"`
	Labels    map[string]string `json:"labels"`
}

// Node 节点信息
type Node struct {
	ID          string            `json:"id"`
	Name        string            `json:"name"`
	Address     string            `json:"address"`
	Status      NodeStatus        `json:"status"`
	CPUUsage    float64           `json:"cpu_usage"`
	MemoryUsage float64           `json:"memory_usage"`
	DiskUsage   float64           `json:"disk_usage"`
	Containers  []*Container      `json:"containers"`
	Labels      map[string]string `json:"labels"`
	LastSeen    time.Time         `json:"last_seen"`
}

// HealthCheck 健康检查配置
type HealthCheck struct {
	Path     string        `json:"path"`
	Interval time.Duration `json:"interval"`
	Timeout  time.Duration `json:"timeout"`
	Retries  int           `json:"retries"`
}

// ContainerStatus 容器状态
type ContainerStatus string

const (
	ContainerStatusCreated    ContainerStatus = "created"
	ContainerStatusRunning    ContainerStatus = "running"
	ContainerStatusPaused     ContainerStatus = "paused"
	ContainerStatusRestarting ContainerStatus = "restarting"
	ContainerStatusRemoving   ContainerStatus = "removing"
	ContainerStatusExited     ContainerStatus = "exited"
	ContainerStatusDead       ContainerStatus = "dead"
)

// NodeStatus 节点状态
type NodeStatus string

const (
	NodeStatusActive   NodeStatus = "active"
	NodeStatusInactive NodeStatus = "inactive"
	NodeStatusDraining NodeStatus = "draining"
	NodeStatusError    NodeStatus = "error"
)

// HealthChecker 健康检查器
type HealthChecker struct {
	orchestrator *ContainerOrchestrator
	interval     time.Duration
	stopChan     chan bool
}

// LoadBalancer 负载均衡器
type LoadBalancer struct {
	orchestrator *ContainerOrchestrator
	strategy     LoadBalanceStrategy
}

// LoadBalanceStrategy 负载均衡策略
type LoadBalanceStrategy string

const (
	StrategyRoundRobin         LoadBalanceStrategy = "round_robin"
	StrategyLeastConnections   LoadBalanceStrategy = "least_connections"
	StrategyWeightedRoundRobin LoadBalanceStrategy = "weighted_round_robin"
	StrategyIPHash             LoadBalanceStrategy = "ip_hash"
)

// Scheduler 调度器
type Scheduler struct {
	orchestrator *ContainerOrchestrator
	strategy     SchedulingStrategy
}

// SchedulingStrategy 调度策略
type SchedulingStrategy string

const (
	SchedulingStrategyRandom     SchedulingStrategy = "random"
	SchedulingStrategyBinPacking SchedulingStrategy = "bin_packing"
	SchedulingStrategySpread     SchedulingStrategy = "spread"
)

// NewContainerOrchestrator 创建新的容器编排器
func NewContainerOrchestrator() (*ContainerOrchestrator, error) {
	dockerClient, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		return nil, fmt.Errorf("failed to create docker client: %w", err)
	}

	orchestrator := &ContainerOrchestrator{
		dockerClient: dockerClient,
		services:     make(map[string]*Service),
		nodes:        make(map[string]*Node),
	}

	// 初始化组件
	orchestrator.healthChecker = NewHealthChecker(orchestrator, 30*time.Second)
	orchestrator.loadBalancer = NewLoadBalancer(orchestrator, StrategyRoundRobin)
	orchestrator.scheduler = NewScheduler(orchestrator, SchedulingStrategyBinPacking)

	return orchestrator, nil
}

// Start 启动编排器
func (o *ContainerOrchestrator) Start() error {
	log.Println("启动容器编排器...")

	// 启动健康检查器
	go o.healthChecker.Start()

	// 启动节点监控
	go o.monitorNodes()

	// 启动服务监控
	go o.monitorServices()

	log.Println("容器编排器已启动")
	return nil
}

// Stop 停止编排器
func (o *ContainerOrchestrator) Stop() error {
	log.Println("停止容器编排器...")

	// 停止健康检查器
	o.healthChecker.Stop()

	// 停止所有服务
	o.mu.Lock()
	for _, service := range o.services {
		o.stopService(service.ID)
	}
	o.mu.Unlock()

	log.Println("容器编排器已停止")
	return nil
}

// CreateService 创建服务
func (o *ContainerOrchestrator) CreateService(service *Service) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	service.ID = generateID()
	service.CreatedAt = time.Now()
	service.UpdatedAt = time.Now()
	service.Containers = make([]*Container, 0)

	o.services[service.ID] = service

	log.Printf("创建服务: %s (ID: %s)", service.Name, service.ID)

	// 部署服务
	return o.deployService(service)
}

// UpdateService 更新服务
func (o *ContainerOrchestrator) UpdateService(serviceID string, updates *Service) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	service, exists := o.services[serviceID]
	if !exists {
		return fmt.Errorf("服务不存在: %s", serviceID)
	}

	// 更新服务配置
	service.Name = updates.Name
	service.Image = updates.Image
	service.Replicas = updates.Replicas
	service.Port = updates.Port
	service.Environment = updates.Environment
	service.Labels = updates.Labels
	service.HealthCheck = updates.HealthCheck
	service.UpdatedAt = time.Now()

	log.Printf("更新服务: %s", service.Name)

	// 重新部署服务
	return o.deployService(service)
}

// DeleteService 删除服务
func (o *ContainerOrchestrator) DeleteService(serviceID string) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	service, exists := o.services[serviceID]
	if !exists {
		return fmt.Errorf("服务不存在: %s", serviceID)
	}

	// 停止服务
	if err := o.stopService(serviceID); err != nil {
		return fmt.Errorf("停止服务失败: %w", err)
	}

	// 删除服务
	delete(o.services, serviceID)

	log.Printf("删除服务: %s", service.Name)
	return nil
}

// ScaleService 扩缩容服务
func (o *ContainerOrchestrator) ScaleService(serviceID string, replicas int) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	service, exists := o.services[serviceID]
	if !exists {
		return fmt.Errorf("服务不存在: %s", serviceID)
	}

	if replicas < 0 {
		return fmt.Errorf("副本数不能为负数")
	}

	oldReplicas := service.Replicas
	service.Replicas = replicas
	service.UpdatedAt = time.Now()

	log.Printf("扩缩容服务 %s: %d -> %d", service.Name, oldReplicas, replicas)

	// 重新部署服务
	return o.deployService(service)
}

// deployService 部署服务
func (o *ContainerOrchestrator) deployService(service *Service) error {
	// 停止现有容器
	for _, container := range service.Containers {
		o.stopContainer(container.ID)
	}
	service.Containers = make([]*Container, 0)

	// 创建新容器
	for i := 0; i < service.Replicas; i++ {
		container, err := o.createContainer(service, i)
		if err != nil {
			log.Printf("创建容器失败: %v", err)
			continue
		}

		service.Containers = append(service.Containers, container)
	}

	return nil
}

// createContainer 创建容器
func (o *ContainerOrchestrator) createContainer(service *Service, index int) (*Container, error) {
	// 选择节点
	node, err := o.scheduler.SelectNode(service)
	if err != nil {
		return nil, fmt.Errorf("选择节点失败: %w", err)
	}

	// 生成容器名称
	containerName := fmt.Sprintf("%s-%d-%s", service.Name, index, generateID()[:8])

	// 构建环境变量
	env := make([]string, 0, len(service.Environment))
	for key, value := range service.Environment {
		env = append(env, fmt.Sprintf("%s=%s", key, value))
	}

	// 创建容器配置
	containerConfig := &container.Config{
		Image: service.Image,
		Env:   env,
		Labels: mergeLabels(service.Labels, map[string]string{
			"orchestrator.service_id":   service.ID,
			"orchestrator.service_name": service.Name,
		}),
	}

	// 创建主机配置
	hostConfig := &container.HostConfig{
		PortBindings: map[string][]string{
			fmt.Sprintf("%d/tcp", service.Port): {fmt.Sprintf("%d", service.Port+index)},
		},
		RestartPolicy: container.RestartPolicy{
			Name: "unless-stopped",
		},
	}

	// 创建网络配置
	networkConfig := &network.NetworkingConfig{}

	// 创建容器
	resp, err := o.dockerClient.ContainerCreate(
		context.Background(),
		containerConfig,
		hostConfig,
		networkConfig,
		nil,
		containerName,
	)
	if err != nil {
		return nil, fmt.Errorf("创建容器失败: %w", err)
	}

	// 启动容器
	if err := o.dockerClient.ContainerStart(
		context.Background(),
		resp.ID,
		types.ContainerStartOptions{},
	); err != nil {
		return nil, fmt.Errorf("启动容器失败: %w", err)
	}

	// 获取容器信息
	containerInfo, err := o.dockerClient.ContainerInspect(context.Background(), resp.ID)
	if err != nil {
		return nil, fmt.Errorf("获取容器信息失败: %w", err)
	}

	// 创建容器对象
	container := &Container{
		ID:        resp.ID,
		ServiceID: service.ID,
		NodeID:    node.ID,
		Name:      containerName,
		Image:     service.Image,
		Status:    ContainerStatus(containerInfo.State.Status),
		Port:      service.Port + index,
		IP:        containerInfo.NetworkSettings.IPAddress,
		CreatedAt: time.Now(),
		Labels:    containerConfig.Labels,
	}

	// 更新节点容器列表
	node.Containers = append(node.Containers, container)

	log.Printf("创建容器: %s (服务: %s, 节点: %s)", containerName, service.Name, node.Name)
	return container, nil
}

// stopContainer 停止容器
func (o *ContainerOrchestrator) stopContainer(containerID string) error {
	// 停止容器
	if err := o.dockerClient.ContainerStop(
		context.Background(),
		containerID,
		container.StopOptions{Timeout: intPtr(30)},
	); err != nil {
		log.Printf("停止容器失败 %s: %v", containerID, err)
	}

	// 删除容器
	if err := o.dockerClient.ContainerRemove(
		context.Background(),
		containerID,
		types.ContainerRemoveOptions{Force: true},
	); err != nil {
		log.Printf("删除容器失败 %s: %v", containerID, err)
	}

	return nil
}

// stopService 停止服务
func (o *ContainerOrchestrator) stopService(serviceID string) error {
	service, exists := o.services[serviceID]
	if !exists {
		return fmt.Errorf("服务不存在: %s", serviceID)
	}

	for _, container := range service.Containers {
		o.stopContainer(container.ID)
	}

	return nil
}

// AddNode 添加节点
func (o *ContainerOrchestrator) AddNode(node *Node) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	node.ID = generateID()
	node.Status = NodeStatusActive
	node.LastSeen = time.Now()
	node.Containers = make([]*Container, 0)

	o.nodes[node.ID] = node

	log.Printf("添加节点: %s (ID: %s)", node.Name, node.ID)
	return nil
}

// RemoveNode 移除节点
func (o *ContainerOrchestrator) RemoveNode(nodeID string) error {
	o.mu.Lock()
	defer o.mu.Unlock()

	node, exists := o.nodes[nodeID]
	if !exists {
		return fmt.Errorf("节点不存在: %s", nodeID)
	}

	// 迁移容器到其他节点
	for _, container := range node.Containers {
		service, exists := o.services[container.ServiceID]
		if exists {
			// 重新创建容器
			o.createContainer(service, len(service.Containers))
		}
	}

	// 删除节点
	delete(o.nodes, nodeID)

	log.Printf("移除节点: %s", node.Name)
	return nil
}

// GetServices 获取服务列表
func (o *ContainerOrchestrator) GetServices() []*Service {
	o.mu.RLock()
	defer o.mu.RUnlock()

	services := make([]*Service, 0, len(o.services))
	for _, service := range o.services {
		services = append(services, service)
	}

	return services
}

// GetService 获取服务
func (o *ContainerOrchestrator) GetService(serviceID string) (*Service, error) {
	o.mu.RLock()
	defer o.mu.RUnlock()

	service, exists := o.services[serviceID]
	if !exists {
		return nil, fmt.Errorf("服务不存在: %s", serviceID)
	}

	return service, nil
}

// GetNodes 获取节点列表
func (o *ContainerOrchestrator) GetNodes() []*Node {
	o.mu.RLock()
	defer o.mu.RUnlock()

	nodes := make([]*Node, 0, len(o.nodes))
	for _, node := range o.nodes {
		nodes = append(nodes, node)
	}

	return nodes
}

// GetNode 获取节点
func (o *ContainerOrchestrator) GetNode(nodeID string) (*Node, error) {
	o.mu.RLock()
	defer o.mu.RUnlock()

	node, exists := o.nodes[nodeID]
	if !exists {
		return nil, fmt.Errorf("节点不存在: %s", nodeID)
	}

	return node, nil
}

// monitorNodes 监控节点
func (o *ContainerOrchestrator) monitorNodes() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		o.mu.Lock()
		for _, node := range o.nodes {
			// 更新节点资源使用情况
			o.updateNodeMetrics(node)
		}
		o.mu.Unlock()
	}
}

// monitorServices 监控服务
func (o *ContainerOrchestrator) monitorServices() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		o.mu.Lock()
		for _, service := range o.services {
			// 检查服务健康状态
			o.checkServiceHealth(service)
		}
		o.mu.Unlock()
	}
}

// updateNodeMetrics 更新节点指标
func (o *ContainerOrchestrator) updateNodeMetrics(node *Node) {
	// 模拟资源使用情况更新
	node.CPUUsage = rand.Float64() * 100
	node.MemoryUsage = rand.Float64() * 100
	node.DiskUsage = rand.Float64() * 100
	node.LastSeen = time.Now()
}

// checkServiceHealth 检查服务健康状态
func (o *ContainerOrchestrator) checkServiceHealth(service *Service) {
	for _, container := range service.Containers {
		// 检查容器状态
		containerInfo, err := o.dockerClient.ContainerInspect(context.Background(), container.ID)
		if err != nil {
			log.Printf("检查容器状态失败 %s: %v", container.ID, err)
			continue
		}

		container.Status = ContainerStatus(containerInfo.State.Status)

		// 如果容器异常退出，尝试重启
		if container.Status == ContainerStatusExited {
			log.Printf("容器异常退出，尝试重启: %s", container.ID)
			o.restartContainer(container.ID)
		}
	}
}

// restartContainer 重启容器
func (o *ContainerOrchestrator) restartContainer(containerID string) error {
	if err := o.dockerClient.ContainerRestart(
		context.Background(),
		containerID,
		container.StopOptions{Timeout: intPtr(30)},
	); err != nil {
		return fmt.Errorf("重启容器失败: %w", err)
	}

	log.Printf("重启容器: %s", containerID)
	return nil
}

// NewHealthChecker 创建健康检查器
func NewHealthChecker(orchestrator *ContainerOrchestrator, interval time.Duration) *HealthChecker {
	return &HealthChecker{
		orchestrator: orchestrator,
		interval:     interval,
		stopChan:     make(chan bool),
	}
}

// Start 启动健康检查器
func (hc *HealthChecker) Start() {
	ticker := time.NewTicker(hc.interval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			hc.checkHealth()
		case <-hc.stopChan:
			return
		}
	}
}

// Stop 停止健康检查器
func (hc *HealthChecker) Stop() {
	close(hc.stopChan)
}

// checkHealth 执行健康检查
func (hc *HealthChecker) checkHealth() {
	hc.orchestrator.mu.RLock()
	services := make([]*Service, 0, len(hc.orchestrator.services))
	for _, service := range hc.orchestrator.services {
		services = append(services, service)
	}
	hc.orchestrator.mu.RUnlock()

	for _, service := range services {
		if service.HealthCheck == nil {
			continue
		}

		for _, container := range service.Containers {
			if container.Status != ContainerStatusRunning {
				continue
			}

			// 执行健康检查
			if !hc.performHealthCheck(container, service.HealthCheck) {
				log.Printf("健康检查失败: %s", container.ID)
				// 可以在这里实现自动重启或标记为不健康
			}
		}
	}
}

// performHealthCheck 执行健康检查
func (hc *HealthChecker) performHealthCheck(container *Container, healthCheck *HealthCheck) bool {
	// 构建健康检查URL
	url := fmt.Sprintf("http://%s:%d%s", container.IP, container.Port, healthCheck.Path)

	// 创建HTTP客户端
	client := &http.Client{
		Timeout: healthCheck.Timeout,
	}

	// 执行健康检查
	resp, err := client.Get(url)
	if err != nil {
		return false
	}
	defer resp.Body.Close()

	return resp.StatusCode == http.StatusOK
}

// NewLoadBalancer 创建负载均衡器
func NewLoadBalancer(orchestrator *ContainerOrchestrator, strategy LoadBalanceStrategy) *LoadBalancer {
	return &LoadBalancer{
		orchestrator: orchestrator,
		strategy:     strategy,
	}
}

// SelectContainer 选择容器
func (lb *LoadBalancer) SelectContainer(serviceID string) (*Container, error) {
	service, err := lb.orchestrator.GetService(serviceID)
	if err != nil {
		return nil, err
	}

	if len(service.Containers) == 0 {
		return nil, fmt.Errorf("服务没有可用的容器")
	}

	// 过滤运行中的容器
	runningContainers := make([]*Container, 0)
	for _, container := range service.Containers {
		if container.Status == ContainerStatusRunning {
			runningContainers = append(runningContainers, container)
		}
	}

	if len(runningContainers) == 0 {
		return nil, fmt.Errorf("服务没有运行中的容器")
	}

	// 根据策略选择容器
	switch lb.strategy {
	case StrategyRoundRobin:
		return lb.selectRoundRobin(runningContainers)
	case StrategyLeastConnections:
		return lb.selectLeastConnections(runningContainers)
	case StrategyWeightedRoundRobin:
		return lb.selectWeightedRoundRobin(runningContainers)
	case StrategyIPHash:
		return lb.selectIPHash(runningContainers)
	default:
		return lb.selectRoundRobin(runningContainers)
	}
}

// selectRoundRobin 轮询选择
func (lb *LoadBalancer) selectRoundRobin(containers []*Container) (*Container, error) {
	index := rand.Intn(len(containers))
	return containers[index], nil
}

// selectLeastConnections 最少连接选择
func (lb *LoadBalancer) selectLeastConnections(containers []*Container) (*Container, error) {
	// 简化实现，实际应该维护连接数统计
	return lb.selectRoundRobin(containers)
}

// selectWeightedRoundRobin 加权轮询选择
func (lb *LoadBalancer) selectWeightedRoundRobin(containers []*Container) (*Container, error) {
	// 简化实现，实际应该根据权重选择
	return lb.selectRoundRobin(containers)
}

// selectIPHash IP哈希选择
func (lb *LoadBalancer) selectIPHash(containers []*Container) (*Container, error) {
	// 简化实现，实际应该根据客户端IP哈希选择
	return lb.selectRoundRobin(containers)
}

// NewScheduler 创建调度器
func NewScheduler(orchestrator *ContainerOrchestrator, strategy SchedulingStrategy) *Scheduler {
	return &Scheduler{
		orchestrator: orchestrator,
		strategy:     strategy,
	}
}

// SelectNode 选择节点
func (s *Scheduler) SelectNode(service *Service) (*Node, error) {
	nodes := s.orchestrator.GetNodes()
	if len(nodes) == 0 {
		return nil, fmt.Errorf("没有可用的节点")
	}

	// 过滤活跃节点
	activeNodes := make([]*Node, 0)
	for _, node := range nodes {
		if node.Status == NodeStatusActive {
			activeNodes = append(activeNodes, node)
		}
	}

	if len(activeNodes) == 0 {
		return nil, fmt.Errorf("没有活跃的节点")
	}

	// 根据策略选择节点
	switch s.strategy {
	case SchedulingStrategyRandom:
		return s.selectRandom(activeNodes)
	case SchedulingStrategyBinPacking:
		return s.selectBinPacking(activeNodes, service)
	case SchedulingStrategySpread:
		return s.selectSpread(activeNodes)
	default:
		return s.selectRandom(activeNodes)
	}
}

// selectRandom 随机选择
func (s *Scheduler) selectRandom(nodes []*Node) (*Node, error) {
	index := rand.Intn(len(nodes))
	return nodes[index], nil
}

// selectBinPacking 装箱算法选择
func (s *Scheduler) selectBinPacking(nodes []*Node, service *Service) (*Node, error) {
	// 选择资源使用率最高的节点（装箱算法）
	bestNode := nodes[0]
	bestScore := s.calculateNodeScore(bestNode)

	for _, node := range nodes[1:] {
		score := s.calculateNodeScore(node)
		if score > bestScore {
			bestScore = score
			bestNode = node
		}
	}

	return bestNode, nil
}

// selectSpread 分散选择
func (s *Scheduler) selectSpread(nodes []*Node) (*Node, error) {
	// 选择容器数量最少的节点（分散算法）
	bestNode := nodes[0]
	minContainers := len(bestNode.Containers)

	for _, node := range nodes[1:] {
		if len(node.Containers) < minContainers {
			minContainers = len(node.Containers)
			bestNode = node
		}
	}

	return bestNode, nil
}

// calculateNodeScore 计算节点分数
func (s *Scheduler) calculateNodeScore(node *Node) float64 {
	// 基于CPU和内存使用率计算分数
	return (node.CPUUsage + node.MemoryUsage) / 2.0
}

// HTTP API 处理器

// setupRoutes 设置路由
func (o *ContainerOrchestrator) setupRoutes() *mux.Router {
	router := mux.NewRouter()

	// 服务相关API
	router.HandleFunc("/api/services", o.handleGetServices).Methods("GET")
	router.HandleFunc("/api/services", o.handleCreateService).Methods("POST")
	router.HandleFunc("/api/services/{id}", o.handleGetService).Methods("GET")
	router.HandleFunc("/api/services/{id}", o.handleUpdateService).Methods("PUT")
	router.HandleFunc("/api/services/{id}", o.handleDeleteService).Methods("DELETE")
	router.HandleFunc("/api/services/{id}/scale", o.handleScaleService).Methods("POST")

	// 节点相关API
	router.HandleFunc("/api/nodes", o.handleGetNodes).Methods("GET")
	router.HandleFunc("/api/nodes", o.handleAddNode).Methods("POST")
	router.HandleFunc("/api/nodes/{id}", o.handleGetNode).Methods("GET")
	router.HandleFunc("/api/nodes/{id}", o.handleRemoveNode).Methods("DELETE")

	// 负载均衡API
	router.HandleFunc("/api/load-balance/{serviceId}", o.handleLoadBalance).Methods("GET")

	return router
}

// handleGetServices 获取服务列表
func (o *ContainerOrchestrator) handleGetServices(w http.ResponseWriter, r *http.Request) {
	services := o.GetServices()
	respondWithJSON(w, http.StatusOK, services)
}

// handleCreateService 创建服务
func (o *ContainerOrchestrator) handleCreateService(w http.ResponseWriter, r *http.Request) {
	var service Service
	if err := json.NewDecoder(r.Body).Decode(&service); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	if err := o.CreateService(&service); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondWithJSON(w, http.StatusCreated, service)
}

// handleGetService 获取服务
func (o *ContainerOrchestrator) handleGetService(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceID := vars["id"]

	service, err := o.GetService(serviceID)
	if err != nil {
		respondWithError(w, http.StatusNotFound, err.Error())
		return
	}

	respondWithJSON(w, http.StatusOK, service)
}

// handleUpdateService 更新服务
func (o *ContainerOrchestrator) handleUpdateService(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceID := vars["id"]

	var updates Service
	if err := json.NewDecoder(r.Body).Decode(&updates); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	if err := o.UpdateService(serviceID, &updates); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	service, _ := o.GetService(serviceID)
	respondWithJSON(w, http.StatusOK, service)
}

// handleDeleteService 删除服务
func (o *ContainerOrchestrator) handleDeleteService(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceID := vars["id"]

	if err := o.DeleteService(serviceID); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]string{"message": "Service deleted successfully"})
}

// handleScaleService 扩缩容服务
func (o *ContainerOrchestrator) handleScaleService(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceID := vars["id"]

	var request struct {
		Replicas int `json:"replicas"`
	}
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	if err := o.ScaleService(serviceID, request.Replicas); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	service, _ := o.GetService(serviceID)
	respondWithJSON(w, http.StatusOK, service)
}

// handleGetNodes 获取节点列表
func (o *ContainerOrchestrator) handleGetNodes(w http.ResponseWriter, r *http.Request) {
	nodes := o.GetNodes()
	respondWithJSON(w, http.StatusOK, nodes)
}

// handleAddNode 添加节点
func (o *ContainerOrchestrator) handleAddNode(w http.ResponseWriter, r *http.Request) {
	var node Node
	if err := json.NewDecoder(r.Body).Decode(&node); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	if err := o.AddNode(&node); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondWithJSON(w, http.StatusCreated, node)
}

// handleGetNode 获取节点
func (o *ContainerOrchestrator) handleGetNode(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeID := vars["id"]

	node, err := o.GetNode(nodeID)
	if err != nil {
		respondWithError(w, http.StatusNotFound, err.Error())
		return
	}

	respondWithJSON(w, http.StatusOK, node)
}

// handleRemoveNode 移除节点
func (o *ContainerOrchestrator) handleRemoveNode(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeID := vars["id"]

	if err := o.RemoveNode(nodeID); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]string{"message": "Node removed successfully"})
}

// handleLoadBalance 负载均衡
func (o *ContainerOrchestrator) handleLoadBalance(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	serviceID := vars["serviceId"]

	container, err := o.loadBalancer.SelectContainer(serviceID)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}

	response := map[string]interface{}{
		"container_id": container.ID,
		"ip":           container.IP,
		"port":         container.Port,
	}

	respondWithJSON(w, http.StatusOK, response)
}

// 辅助函数

// respondWithJSON 返回JSON响应
func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	response, _ := json.Marshal(payload)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(response)
}

// respondWithError 返回错误响应
func respondWithError(w http.ResponseWriter, code int, message string) {
	respondWithJSON(w, code, map[string]string{"error": message})
}

// generateID 生成ID
func generateID() string {
	return fmt.Sprintf("%d", time.Now().UnixNano())
}

// intPtr 返回int指针
func intPtr(i int) *int {
	return &i
}

// mergeLabels 合并标签
func mergeLabels(labels1, labels2 map[string]string) map[string]string {
	result := make(map[string]string)
	for k, v := range labels1 {
		result[k] = v
	}
	for k, v := range labels2 {
		result[k] = v
	}
	return result
}

// 主函数
func main() {
	// 创建编排器
	orchestrator, err := NewContainerOrchestrator()
	if err != nil {
		log.Fatalf("创建编排器失败: %v", err)
	}

	// 启动编排器
	if err := orchestrator.Start(); err != nil {
		log.Fatalf("启动编排器失败: %v", err)
	}
	defer orchestrator.Stop()

	// 添加示例节点
	node := &Node{
		Name:    "node-01",
		Address: "192.168.1.100",
		Labels:  map[string]string{"zone": "us-west-1", "type": "compute"},
	}
	orchestrator.AddNode(node)

	// 创建示例服务
	service := &Service{
		Name:     "web-server",
		Image:    "nginx:latest",
		Replicas: 3,
		Port:     80,
		Environment: map[string]string{
			"ENV": "production",
		},
		Labels: map[string]string{
			"app": "web",
		},
		HealthCheck: &HealthCheck{
			Path:     "/health",
			Interval: 30 * time.Second,
			Timeout:  5 * time.Second,
			Retries:  3,
		},
	}
	orchestrator.CreateService(service)

	// 设置HTTP服务器
	router := orchestrator.setupRoutes()
	server := &http.Server{
		Addr:    ":8080",
		Handler: router,
	}

	log.Println("容器编排器HTTP服务器启动在 :8080")
	log.Fatal(server.ListenAndServe())
}
