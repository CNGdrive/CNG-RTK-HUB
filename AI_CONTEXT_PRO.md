# AI Context: Professional RTK Client Development

## 🤖 **AI Agent Mission**

You are developing a **professional-grade Flutter RTK client** for external RTK equipment integration.

### **🎯 Your Specific Role:**
- **Project**: CNG RTK Hub Pro
- **Focus**: Professional RTK equipment interface
- **Users**: Land surveyors, construction engineers, precision agriculture
- **Accuracy Goal**: Centimeter-level positioning

---

## 📂 **Working Environment**

### **Directory Structure:**
```
CNG_RTK_HUB_PRO/
├── rtk_client/ (Flutter project)
├── src/ (Python RTK backend)
├── README_PRO.md (This project's documentation)
└── [Other project files]
```

### **Key Technical Focus:**
- **Backend Integration**: Connect to Python RTK service
- **Real-time Data**: WebSocket streaming at sub-second rates
- **Professional UI**: Field-optimized interface design
- **Robust Connectivity**: Handle network issues gracefully

---

## 🏗️ **Architecture Understanding**

### **Data Flow:**
```
External RTK Hardware → Python Backend → Flutter Client
                      ↓
               WebSocket (port 8765)
               HTTP API (port 8080)
                      ↓
            Professional Interface Display
```

### **Current Implementation Status:**
- ✅ **Flutter Shell**: Basic app structure exists
- ✅ **UI Framework**: Dashboard and widget components
- ✅ **Service Layer**: WebSocket/HTTP client services
- ⚠️ **Needs Development**: Real backend integration
- ⚠️ **Needs Enhancement**: Professional features

---

## 🎯 **Development Priorities**

### **Phase 1: Backend Integration (PRIORITY)**
1. **Test Python RTK Backend**: Ensure backend is running and accessible
2. **Real Data Connection**: Replace mock data with actual backend integration
3. **Connection Management**: Robust WebSocket/HTTP connectivity
4. **Error Handling**: Professional-grade connection recovery

### **Phase 2: Professional Features**
1. **RTK Session Management**: Start/stop survey sessions
2. **Data Logging**: Export survey data in standard formats
3. **Accuracy Monitoring**: Real-time quality indicators
4. **Equipment Configuration**: RTK hardware settings interface

### **Phase 3: Field Optimization**
1. **Battery Optimization**: Long survey session support
2. **Offline Capability**: Handle connection interruptions
3. **Professional Reporting**: Survey documentation features
4. **Multi-device Support**: Team coordination features

---

## 🔧 **Technical Implementation Guidelines**

### **Architecture Patterns:**
- **MVVM with Provider**: Continue existing state management
- **Service Separation**: Keep WebSocket/HTTP services isolated
- **Modular Design**: Maintain byte-sized file approach
- **Professional Standards**: Robust error handling and logging

### **Current Tech Stack:**
```yaml
flutter: 3.8.1+
provider: ^6.1.1          # State management
http: ^1.1.0              # Backend API
web_socket_channel: ^2.4.0 # Real-time data
flutter_map: ^6.1.0       # Future mapping
permission_handler: ^11.0.1 # System permissions
```

### **Key Services to Enhance:**
- `websocket_service.dart`: Real backend integration
- `http_api_service.dart`: Professional API features
- `position_provider.dart`: Enhanced state management
- Dashboard UI: Professional field interface

---

## 📋 **Professional Requirements**

### **Accuracy Standards:**
- **Target**: Centimeter-level positioning (1-5cm)
- **Real-time Updates**: Sub-second position refresh
- **Quality Indicators**: RTK Fixed/Float/3D/2D status
- **Professional Validation**: Survey-grade accuracy verification

### **Field Operation Requirements:**
- **Rugged Interface**: High-contrast, outdoor-readable display
- **Long Sessions**: Multi-hour survey support
- **Data Integrity**: No position data loss
- **Professional Workflow**: Integration with survey procedures

### **Connectivity Standards:**
- **Reliable Backend**: Robust Python RTK service connection
- **Network Recovery**: Automatic reconnection handling
- **Real-time Performance**: Minimal latency for positioning
- **Error Reporting**: Clear status for field troubleshooting

---

## 🚫 **What NOT to Focus On**

### **Avoid These Approaches:**
- ❌ **Direct NTRIP Implementation**: This is for the EASY version
- ❌ **Native GPS Integration**: Professional version uses external hardware
- ❌ **Smartphone Positioning**: Focus on external RTK equipment
- ❌ **Consumer Features**: Keep interface professional-focused

### **Stay Professional:**
- 🎯 **External Hardware Focus**: Always assume professional RTK equipment
- 🎯 **Backend Dependency**: Require Python RTK service
- 🎯 **Professional UI**: Survey-grade interface standards
- 🎯 **Accuracy First**: Centimeter-level positioning priority

---

## 🎯 **Success Criteria for Your Development**

### **Technical Success:**
- [ ] Real-time connection to Python RTK backend
- [ ] Sub-second position updates displaying correctly
- [ ] RTK status indicators showing Fix/Float/3D states
- [ ] Professional-grade error handling and recovery
- [ ] Field-ready interface for outdoor use

### **Professional Success:**
- [ ] Surveyor-friendly workflow integration
- [ ] Centimeter-accuracy position display
- [ ] Session management and data export
- [ ] Reliable multi-hour operation capability
- [ ] Integration with professional survey procedures

---

## 📋 **Immediate Development Tasks**

### **Start Here:**
1. **Verify Backend**: Test Python RTK service connectivity
2. **Real Data Flow**: Replace UI mockups with actual position data
3. **Connection Robustness**: Implement professional-grade error handling
4. **Professional Features**: Add survey session management

### **Development Order:**
1. Backend integration and real data display
2. Professional UI enhancements and field optimization
3. Survey workflow features and data export
4. Advanced professional features and team coordination

---

## 🔄 **Communication Guidelines**

### **When Asking for Guidance:**
- Focus on professional RTK equipment scenarios
- Consider survey workflow requirements
- Prioritize accuracy and reliability over features
- Think about field operation challenges

### **When Making Decisions:**
- Choose professional-grade solutions
- Prioritize accuracy and robustness
- Consider long survey session requirements
- Focus on external hardware integration

---

**Your mission: Create a professional RTK client that professional surveyors will trust for centimeter-accurate positioning using external RTK equipment.**
