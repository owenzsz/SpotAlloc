package logger

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sync"
	"time"
)

var (
	globalLogger *Logger
	once         sync.Once
)

func InitLogger(logDir, logFileName string) error {
	var err error
	once.Do(func() {
		globalLogger, err = NewLogger(logDir, logFileName)
	})
	return err
}

func Info(message string, data map[string]interface{}) {
	if globalLogger != nil {
		globalLogger.Info(message, data)
	}
}

func Warning(message string, data map[string]interface{}) {
	if globalLogger != nil {
		globalLogger.Warning(message, data)
	}
}

func Error(message string, data map[string]interface{}) {
	if globalLogger != nil {
		globalLogger.Error(message, data)
	}
}

func CloseLogger() {
	if globalLogger != nil {
		globalLogger.Close()
	}
}

type Logger struct {
	logger *log.Logger
	file   *os.File
}

func NewLogger(logDir, logFileName string) (*Logger, error) {
	if err := os.MkdirAll(logDir, os.ModePerm); err != nil {
		return nil, fmt.Errorf("failed to create log directory: %v", err)
	}

	logFile := filepath.Join(logDir, logFileName)
	file, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		return nil, fmt.Errorf("failed to open log file: %v", err)
	}

	logger := log.New(file, "", log.LstdFlags)

	return &Logger{
		logger: logger,
		file:   file,
	}, nil
}

func (l *Logger) Close() {
	if l.file != nil {
		l.file.Close()
	}
}

func (l *Logger) Info(message string, data map[string]interface{}) {
	l.log("INFO", message, data)
}

func (l *Logger) Warning(message string, data map[string]interface{}) {
	l.log("WARNING", message, data)
}

func (l *Logger) Error(message string, data map[string]interface{}) {
	l.log("ERROR", message, data)
}

func (l *Logger) log(level, message string, data map[string]interface{}) {
	logData := map[string]interface{}{
		"timestamp": time.Now().Format(time.RFC3339),
		"level":     level,
		"message":   message,
		"data":      data,
	}

	jsonData, err := json.Marshal(logData)
	if err != nil {
		l.logger.Printf("Failed to marshal log data: %v", err)
		return
	}

	l.logger.Println(string(jsonData))
}
