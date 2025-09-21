# Web UI界面原型设计

## 摘要

本文档介绍了语义模型验证工具的Web UI界面原型设计，包括用户界面设计、交互流程、技术架构和实现方案。
通过现代化的Web界面，为用户提供直观、易用的语义模型验证体验。

## 1. 界面设计原则

### 1.1 设计理念

- **简洁直观**：界面简洁明了，操作流程直观
- **功能完整**：覆盖语义模型验证的完整流程
- **响应式设计**：支持多种设备和屏幕尺寸
- **可访问性**：符合WCAG 2.1可访问性标准

### 1.2 用户体验目标

- 降低学习成本，新用户5分钟内上手
- 提高验证效率，常用操作3步内完成
- 提供实时反馈，验证结果即时显示
- 支持协作功能，团队共享验证结果

## 2. 界面架构设计

### 2.1 整体布局

```text
┌─────────────────────────────────────────────────────────┐
│                    Header Navigation                     │
├─────────────────────────────────────────────────────────┤
│ Sidebar │              Main Content Area                │
│         │                                               │
│  Model  │  ┌─────────────────────────────────────────┐  │
│  List   │  │         Model Editor                    │  │
│         │  │                                         │  │
│  Verify │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │  │
│  History│  │  │  Code   │ │ Visual  │ │ Config  │   │  │
│         │  │  │ Editor  │ │ Editor  │ │ Editor  │   │  │
│  Tools  │  │  └─────────┘ └─────────┘ └─────────┘   │  │
│         │  └─────────────────────────────────────────┘  │
│  Help   │                                               │
│         │  ┌─────────────────────────────────────────┐  │
│         │  │         Verification Results            │  │
│         │  │                                         │  │
│         │  │  ✓ Passed  ✗ Failed  ⚠ Warnings        │  │
│         │  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 组件层次结构

```text
App
├── Header
│   ├── Logo
│   ├── Navigation
│   └── UserMenu
├── Sidebar
│   ├── ModelList
│   ├── VerificationHistory
│   ├── Tools
│   └── Help
└── MainContent
    ├── ModelEditor
    │   ├── CodeEditor
    │   ├── VisualEditor
    │   └── ConfigEditor
    ├── VerificationPanel
    │   ├── VerificationSettings
    │   ├── ProgressIndicator
    │   └── ResultsDisplay
    └── OutputPanel
        ├── Results
        ├── Logs
        └── Reports
```

## 3. 核心功能界面

### 3.1 模型编辑器界面

#### 3.1.1 代码编辑器

```typescript
interface CodeEditorProps {
  model: SemanticModel;
  onChange: (model: SemanticModel) => void;
  onValidate: () => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ model, onChange, onValidate }) => {
  return (
    <div className="code-editor">
      <div className="editor-header">
        <h3>语义模型代码编辑器</h3>
        <div className="editor-actions">
          <button onClick={onValidate} className="btn-primary">
            验证模型
          </button>
          <button className="btn-secondary">
            格式化
          </button>
        </div>
      </div>
      <MonacoEditor
        language="semantic-model"
        value={model.code}
        onChange={(value) => onChange({ ...model, code: value })}
        options={{
          minimap: { enabled: false },
          wordWrap: 'on',
          lineNumbers: 'on',
          folding: true,
          autoIndent: 'full'
        }}
      />
      <div className="editor-status">
        <span className="status-indicator">●</span>
        <span>模型已保存</span>
      </div>
    </div>
  );
};
```

#### 3.1.2 可视化编辑器

```typescript
interface VisualEditorProps {
  model: SemanticModel;
  onChange: (model: SemanticModel) => void;
}

const VisualEditor: React.FC<VisualEditorProps> = ({ model, onChange }) => {
  return (
    <div className="visual-editor">
      <div className="editor-toolbar">
        <div className="tool-group">
          <button className="tool-btn" title="添加状态">
            <Icon name="state" />
          </button>
          <button className="tool-btn" title="添加操作">
            <Icon name="operation" />
          </button>
          <button className="tool-btn" title="添加关系">
            <Icon name="relation" />
          </button>
        </div>
        <div className="tool-group">
          <button className="tool-btn" title="选择">
            <Icon name="select" />
          </button>
          <button className="tool-btn" title="移动">
            <Icon name="move" />
          </button>
          <button className="tool-btn" title="删除">
            <Icon name="delete" />
          </button>
        </div>
      </div>
      <div className="canvas-container">
        <svg className="model-canvas">
          {/* 状态节点 */}
          {model.states.map(state => (
            <g key={state.id} className="state-node">
              <rect
                x={state.x}
                y={state.y}
                width={state.width}
                height={state.height}
                rx="5"
                className="state-rect"
              />
              <text
                x={state.x + state.width / 2}
                y={state.y + state.height / 2}
                textAnchor="middle"
                className="state-label"
              >
                {state.name}
              </text>
            </g>
          ))}
          
          {/* 关系连线 */}
          {model.relations.map(relation => (
            <line
              key={relation.id}
              x1={relation.source.x}
              y1={relation.source.y}
              x2={relation.target.x}
              y2={relation.target.y}
              className="relation-line"
            />
          ))}
        </svg>
      </div>
    </div>
  );
};
```

### 3.2 验证面板界面

```typescript
interface VerificationPanelProps {
  model: SemanticModel;
  onVerify: (settings: VerificationSettings) => void;
  results: VerificationResult[];
}

const VerificationPanel: React.FC<VerificationPanelProps> = ({ 
  model, 
  onVerify, 
  results 
}) => {
  const [settings, setSettings] = useState<VerificationSettings>({
    solver: 'z3',
    timeout: 30,
    verbose: false,
    checks: ['consistency', 'correctness', 'completeness']
  });

  return (
    <div className="verification-panel">
      <div className="panel-header">
        <h3>语义模型验证</h3>
      </div>
      
      <div className="verification-settings">
        <div className="setting-group">
          <label>SMT求解器</label>
          <select 
            value={settings.solver}
            onChange={(e) => setSettings({...settings, solver: e.target.value})}
          >
            <option value="z3">Z3</option>
            <option value="cvc5">CVC5</option>
            <option value="both">Z3 + CVC5</option>
          </select>
        </div>
        
        <div className="setting-group">
          <label>超时时间 (秒)</label>
          <input
            type="number"
            value={settings.timeout}
            onChange={(e) => setSettings({...settings, timeout: parseInt(e.target.value)})}
            min="1"
            max="300"
          />
        </div>
        
        <div className="setting-group">
          <label>验证检查项</label>
          <div className="checkbox-group">
            {['consistency', 'correctness', 'completeness'].map(check => (
              <label key={check} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={settings.checks.includes(check)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSettings({...settings, checks: [...settings.checks, check]});
                    } else {
                      setSettings({...settings, checks: settings.checks.filter(c => c !== check)});
                    }
                  }}
                />
                {check}
              </label>
            ))}
          </div>
        </div>
      </div>
      
      <div className="verification-actions">
        <button 
          className="btn-primary btn-large"
          onClick={() => onVerify(settings)}
        >
          开始验证
        </button>
      </div>
      
      <div className="verification-results">
        {results.map((result, index) => (
          <VerificationResultCard key={index} result={result} />
        ))}
      </div>
    </div>
  );
};
```

### 3.3 结果展示界面

```typescript
interface VerificationResultCardProps {
  result: VerificationResult;
}

const VerificationResultCard: React.FC<VerificationResultCardProps> = ({ result }) => {
  return (
    <div className={`result-card ${result.status}`}>
      <div className="result-header">
        <div className="result-status">
          <Icon name={result.status === 'passed' ? 'check' : 'error'} />
          <span className="status-text">
            {result.status === 'passed' ? '验证通过' : '验证失败'}
          </span>
        </div>
        <div className="result-meta">
          <span className="solver-name">{result.solver}</span>
          <span className="verification-time">{result.duration}ms</span>
        </div>
      </div>
      
      <div className="result-details">
        <div className="result-summary">
          <div className="summary-item">
            <span className="label">检查项:</span>
            <span className="value">{result.checks.join(', ')}</span>
          </div>
          <div className="summary-item">
            <span className="label">状态:</span>
            <span className={`value status-${result.status}`}>
              {result.status === 'passed' ? '通过' : '失败'}
            </span>
          </div>
        </div>
        
        {result.violations.length > 0 && (
          <div className="violations">
            <h4>违规项</h4>
            {result.violations.map((violation, index) => (
              <div key={index} className="violation-item">
                <div className="violation-header">
                  <span className="violation-type">{violation.type}</span>
                  <span className={`violation-severity ${violation.severity}`}>
                    {violation.severity}
                  </span>
                </div>
                <div className="violation-message">
                  {violation.message}
                </div>
                {violation.suggestion && (
                  <div className="violation-suggestion">
                    建议: {violation.suggestion}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
```

## 4. 技术实现方案

### 4.1 前端技术栈

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "typescript": "^4.9.0",
    "monaco-editor": "^0.44.0",
    "d3": "^7.8.0",
    "antd": "^5.0.0",
    "axios": "^1.3.0",
    "react-router-dom": "^6.8.0",
    "zustand": "^4.3.0",
    "react-query": "^3.39.0"
  },
  "devDependencies": {
    "vite": "^4.1.0",
    "@types/react": "^18.0.0",
    "@types/d3": "^7.4.0",
    "tailwindcss": "^3.2.0",
    "eslint": "^8.34.0",
    "prettier": "^2.8.0"
  }
}
```

### 4.2 状态管理

```typescript
import { create } from 'zustand';

interface AppState {
  // 模型状态
  currentModel: SemanticModel | null;
  models: SemanticModel[];
  
  // 验证状态
  verificationResults: VerificationResult[];
  isVerifying: boolean;
  
  // UI状态
  activeTab: 'code' | 'visual' | 'config';
  sidebarCollapsed: boolean;
  
  // 操作
  setCurrentModel: (model: SemanticModel) => void;
  addModel: (model: SemanticModel) => void;
  updateModel: (id: string, updates: Partial<SemanticModel>) => void;
  deleteModel: (id: string) => void;
  
  startVerification: () => void;
  finishVerification: (results: VerificationResult[]) => void;
  
  setActiveTab: (tab: 'code' | 'visual' | 'config') => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  currentModel: null,
  models: [],
  verificationResults: [],
  isVerifying: false,
  activeTab: 'code',
  sidebarCollapsed: false,
  
  setCurrentModel: (model) => set({ currentModel: model }),
  
  addModel: (model) => set((state) => ({
    models: [...state.models, model],
    currentModel: model
  })),
  
  updateModel: (id, updates) => set((state) => ({
    models: state.models.map(model => 
      model.id === id ? { ...model, ...updates } : model
    ),
    currentModel: state.currentModel?.id === id 
      ? { ...state.currentModel, ...updates }
      : state.currentModel
  })),
  
  deleteModel: (id) => set((state) => ({
    models: state.models.filter(model => model.id !== id),
    currentModel: state.currentModel?.id === id ? null : state.currentModel
  })),
  
  startVerification: () => set({ isVerifying: true }),
  
  finishVerification: (results) => set({ 
    verificationResults: results,
    isVerifying: false
  }),
  
  setActiveTab: (tab) => set({ activeTab: tab }),
  
  toggleSidebar: () => set((state) => ({ 
    sidebarCollapsed: !state.sidebarCollapsed 
  }))
}));
```

### 4.3 API集成

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
});

export interface SemanticModelAPI {
  // 模型管理
  getModels: () => Promise<SemanticModel[]>;
  getModel: (id: string) => Promise<SemanticModel>;
  createModel: (model: SemanticModel) => Promise<SemanticModel>;
  updateModel: (id: string, model: SemanticModel) => Promise<SemanticModel>;
  deleteModel: (id: string) => Promise<void>;
  
  // 验证
  verifyModel: (modelId: string, settings: VerificationSettings) => Promise<VerificationResult[]>;
  getVerificationHistory: (modelId: string) => Promise<VerificationResult[]>;
  
  // 工具
  formatModel: (model: SemanticModel) => Promise<SemanticModel>;
  validateSyntax: (model: SemanticModel) => Promise<ValidationResult>;
}

export const semanticModelAPI: SemanticModelAPI = {
  getModels: () => api.get('/models').then(res => res.data),
  
  getModel: (id) => api.get(`/models/${id}`).then(res => res.data),
  
  createModel: (model) => api.post('/models', model).then(res => res.data),
  
  updateModel: (id, model) => api.put(`/models/${id}`, model).then(res => res.data),
  
  deleteModel: (id) => api.delete(`/models/${id}`),
  
  verifyModel: (modelId, settings) => 
    api.post(`/models/${modelId}/verify`, settings).then(res => res.data),
  
  getVerificationHistory: (modelId) => 
    api.get(`/models/${modelId}/verification-history`).then(res => res.data),
  
  formatModel: (model) => 
    api.post('/tools/format', model).then(res => res.data),
  
  validateSyntax: (model) => 
    api.post('/tools/validate-syntax', model).then(res => res.data)
};
```

## 5. 响应式设计

### 5.1 移动端适配

```css
/* 移动端样式 */
@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }
  
  .sidebar {
    position: fixed;
    top: 0;
    left: -100%;
    width: 80%;
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s ease;
  }
  
  .sidebar.open {
    left: 0;
  }
  
  .main-content {
    width: 100%;
    padding: 1rem;
  }
  
  .editor-tabs {
    flex-direction: column;
  }
  
  .verification-panel {
    margin-top: 1rem;
  }
}

/* 平板端样式 */
@media (min-width: 769px) and (max-width: 1024px) {
  .sidebar {
    width: 250px;
  }
  
  .main-content {
    width: calc(100% - 250px);
  }
  
  .editor-container {
    flex-direction: column;
  }
}
```

### 5.2 可访问性支持

```typescript
// 键盘导航支持
const useKeyboardNavigation = () => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + S: 保存模型
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        saveModel();
      }
      
      // Ctrl/Cmd + V: 开始验证
      if ((event.ctrlKey || event.metaKey) && event.key === 'v') {
        event.preventDefault();
        startVerification();
      }
      
      // F1: 显示帮助
      if (event.key === 'F1') {
        event.preventDefault();
        showHelp();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
};

// 屏幕阅读器支持
const AccessibleButton: React.FC<{
  onClick: () => void;
  children: React.ReactNode;
  ariaLabel?: string;
}> = ({ onClick, children, ariaLabel }) => {
  return (
    <button
      onClick={onClick}
      aria-label={ariaLabel}
      className="accessible-button"
    >
      {children}
    </button>
  );
};
```

## 6. 部署配置

### 6.1 Docker配置

```dockerfile
# 前端构建
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# 生产环境
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 6.2 Nginx配置

```nginx
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API代理
    location /api/ {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # SPA路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 7. 结论

本文档介绍了语义模型验证工具的Web UI界面原型设计，主要特点包括：

1. **现代化设计**：采用React + TypeScript技术栈，提供现代化的用户界面
2. **功能完整**：覆盖语义模型编辑、验证、结果展示的完整流程
3. **响应式布局**：支持桌面、平板、移动端多种设备
4. **可访问性**：符合WCAG 2.1标准，支持键盘导航和屏幕阅读器
5. **易于部署**：提供Docker和Nginx配置，支持容器化部署

这个Web UI原型为用户提供了直观、高效的语义模型验证体验，大大降低了工具的使用门槛。

## 参考文献

1. React Documentation. (2023). React - A JavaScript library for building user interfaces.
2. TypeScript Documentation. (2023). TypeScript - JavaScript with syntax for types.
3. Monaco Editor. (2023). The Monaco Editor - Code editor for the web.
4. Ant Design. (2023). A design system for enterprise-level products.

---

*本文档基于2025年最新Web技术发展，提供了完整的UI界面原型设计方案。*
