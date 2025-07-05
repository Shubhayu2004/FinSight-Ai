# AI Finance Agent Frontend

A modern React-based frontend for the AI Finance Agent system, featuring both company data analysis and annual report processing with the fine-tuned FinAgent model.

## 🎯 Features

### **Company Data Analysis**
- Browse and search Indian companies from BSE/NSE
- View detailed company information
- Download annual reports

### **Annual Report Analysis with FinAgent**
- **File Upload**: Drag & drop or select PDF files
- **PDF Processing**: Extract text, sections, and financial data
- **AI Analysis**: Query the fine-tuned FinAgent model
- **Real-time Results**: Get instant financial insights
- **Batch Processing**: Process multiple reports at once
- **Model Monitoring**: Check FinAgent model status

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start the Frontend
```bash
npm start
```

The application will open at `http://localhost:3000`

### 3. Start the Backend
Make sure the backend API is running:
```bash
cd backend
uvicorn api.annual_report_api:app --reload
```

## 📱 Interface Overview

### **Navigation**
The app has two main sections accessible via tabs:
- **Company Data**: Browse and search companies
- **Annual Report Analysis**: Upload and analyze reports with FinAgent

### **Annual Report Analyzer Features**

#### **1. Model Status Dashboard**
- View FinAgent model information
- Check model availability and device
- Test the model with sample data

#### **2. File Management**
- **Upload PDFs**: Select annual report files
- **File List**: View all uploaded files
- **Process Reports**: Extract data and create chunks
- **Batch Processing**: Process all files at once
- **Delete Files**: Remove unwanted files

#### **3. AI Analysis**
- **Select File**: Choose which report to analyze
- **Enter Company Name**: Optional company identification
- **Ask Questions**: Natural language queries about the report
- **View Results**: Get detailed FinAgent analysis

#### **4. Sample Questions**
The interface includes suggested questions:
- Financial Performance: "What was the company's revenue and profit performance?"
- Market Analysis: "How did the company perform in international markets?"
- Risk Assessment: "What are the main risk factors mentioned in the report?"
- Strategy: "What are the key strategic initiatives for the coming year?"
- Growth: "What were the main drivers of revenue growth?"
- ESG: "What ESG initiatives were highlighted in the report?"

## 🎨 UI Components

### **Status Messages**
- **Success**: Green background for successful operations
- **Error**: Red background for errors and failures
- **Info**: Blue background for informational messages

### **Loading States**
- Spinning indicators during processing
- Disabled buttons to prevent multiple requests
- Progress feedback for long operations

### **Responsive Design**
- Mobile-friendly interface
- Adaptive layouts for different screen sizes
- Touch-friendly controls

## 🔧 Configuration

### **API Configuration**
The frontend is configured to connect to the backend at `http://localhost:8000`. You can modify this in `AnnualReportAnalyzer.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### **Proxy Configuration**
The `package.json` includes a proxy configuration to handle CORS:

```json
{
  "proxy": "http://localhost:8000"
}
```

## 📊 Usage Examples

### **1. Upload and Process a Report**
1. Click "Choose PDF File" in the upload section
2. Select an annual report PDF
3. Click "Process" to extract data
4. View processing results and statistics

### **2. Ask FinAgent Questions**
1. Select a processed file from the dropdown
2. Optionally enter the company name
3. Type your question in the text area
4. Click "Ask FinAgent" to get analysis
5. View the detailed response

### **3. Batch Process Multiple Reports**
1. Upload multiple PDF files
2. Click "Process All Files" to process them simultaneously
3. Monitor progress and results

### **4. Test FinAgent Model**
1. Click "Test FinAgent" to verify model functionality
2. View model information and status
3. Check if the model is responding correctly

## 🛠️ Development

### **Available Scripts**
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject from Create React App
npm run eject
```

### **File Structure**
```
src/
├── App.js                 # Main app component with navigation
├── App.css               # Global styles and component styles
├── Companies.js          # Company data browser component
├── AnnualReportAnalyzer.js # Annual report analysis component
├── index.js              # App entry point
└── index.css             # Global styles
```

### **Component Architecture**
- **App.js**: Main container with tab navigation
- **Companies.js**: Company data browsing interface
- **AnnualReportAnalyzer.js**: Complete annual report analysis interface

## 🔍 API Integration

The frontend integrates with these backend endpoints:

### **File Management**
- `POST /upload-pdf` - Upload PDF files
- `GET /uploaded-files` - List uploaded files
- `DELETE /uploaded-files/{filename}` - Delete files

### **Processing**
- `POST /process-report` - Process individual report
- `POST /batch-process` - Process all reports

### **Analysis**
- `POST /query-report` - Query FinAgent about reports
- `POST /test-finagent` - Test FinAgent model

### **Information**
- `GET /model-info` - Get FinAgent model information
- `GET /stats` - Get processing statistics
- `GET /health` - Check system health

## 🎯 Best Practices

### **File Upload**
- Only PDF files are accepted
- Large files may take time to upload
- Check file size before uploading

### **Processing**
- Processing creates cached data for faster subsequent queries
- Use "Process All Files" for multiple reports
- Monitor status messages for progress

### **Querying**
- Be specific in your questions for better results
- Include company context when relevant
- Use the sample questions as starting points

### **Performance**
- The interface includes loading states for all operations
- Large reports may take time to process
- Results are cached for faster subsequent queries

## 🐛 Troubleshooting

### **Common Issues**

1. **Backend Not Running**
   - Ensure the backend API is running on port 8000
   - Check the console for connection errors

2. **File Upload Fails**
   - Verify the file is a valid PDF
   - Check file size (should be reasonable)
   - Ensure backend upload directory is writable

3. **Processing Fails**
   - Check if the PDF contains extractable text
   - Verify the backend has necessary dependencies
   - Check backend logs for detailed errors

4. **FinAgent Not Responding**
   - Test the model using "Test FinAgent" button
   - Check model information for status
   - Verify the model path is correct

5. **CORS Errors**
   - The proxy configuration should handle this
   - Ensure backend allows requests from frontend origin

### **Debug Mode**
Enable browser developer tools to see:
- Network requests and responses
- Console errors and warnings
- API call details

## 📈 Future Enhancements

Potential improvements for the frontend:
- **Real-time Processing**: WebSocket updates for long operations
- **Advanced Search**: Filter and search uploaded reports
- **Export Results**: Download analysis results as PDF/CSV
- **Comparison Tools**: Compare multiple reports side-by-side
- **Visualizations**: Charts and graphs for financial data
- **User Authentication**: Secure access to reports and analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
