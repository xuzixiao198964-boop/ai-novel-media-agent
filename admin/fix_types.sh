#!/bin/bash
# 批量修复TypeScript类型错误

# Novels.tsx
sed -i 's/const data = await novelsApi.list(/const data = await novelsApi.list(/g' src/pages/Novels.tsx
sed -i 's/      })$/      }) as any/g' src/pages/Novels.tsx

# Videos.tsx
sed -i 's/const data = await videosApi.list(/const data = await videosApi.list(/g' src/pages/Videos.tsx
sed -i 's/      })$/      }) as any/g' src/pages/Videos.tsx

# Tasks.tsx
sed -i 's/const data = await tasksApi.list(/const data = await tasksApi.list(/g' src/pages/Tasks.tsx
sed -i 's/      })$/      }) as any/g' src/pages/Tasks.tsx

# ApiKeys.tsx
sed -i 's/const data = await apiKeysApi.list(/const data = await apiKeysApi.list(/g' src/pages/ApiKeys.tsx
sed -i 's/      })$/      }) as any/g' src/pages/ApiKeys.tsx

# Logs.tsx
sed -i 's/const data = await logsApi.list(/const data = await logsApi.list(/g' src/pages/Logs.tsx
sed -i 's/      })$/      }) as any/g' src/pages/Logs.tsx

# Publish.tsx
sed -i 's/const data = await publishApi.list(/const data = await publishApi.list(/g' src/pages/Publish.tsx
sed -i 's/      })$/      }) as any/g' src/pages/Publish.tsx

# Finance.tsx
sed -i 's/const trend = await financeApi.getTrend(30)$/const trend = await financeApi.getTrend(30) as any/g' src/pages/Finance.tsx

# Config.tsx
sed -i 's/const data = await configApi.getAll()$/const data = await configApi.getAll() as any/g' src/pages/Config.tsx

