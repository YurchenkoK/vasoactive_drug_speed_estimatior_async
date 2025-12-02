package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// Константы для конфигурации
const (
	DJANGO_SERVICE_URL = "http://localhost:8000"
	SECRET_KEY         = "a1b2c3d4e5f6g7h8"
	PORT               = ":8081"
)

// Структура одного препарата в запросе
type DrugData struct {
	DrugInOrderID     int     `json:"druginorder_id" binding:"required"`
	DrugConcentration float64 `json:"drug_concentration" binding:"required"`
	AmpouleVolume     float64 `json:"ampoule_volume" binding:"required"`
	AmpoulesCount     int     `json:"ampoules_count" binding:"required"`
	SolventVolume     float64 `json:"solvent_volume" binding:"required"`
	PatientWeight     float64 `json:"patient_weight" binding:"required"`
}

// Структура запроса от Django
type DrugsProcessRequest struct {
	OrderID int        `json:"order_id" binding:"required"`
	Drugs   []DrugData `json:"drugs" binding:"required"`
}

// Структура результата для одного препарата
type DrugResult struct {
	DrugInOrderID  int     `json:"druginorder_id"`
	InfusionSpeed  float64 `json:"infusion_speed"`
}

// Структура для отправки результатов обратно в Django
type ResultsData struct {
	SecretKey string       `json:"secret_key"`
	OrderID   int          `json:"order_id"`
	Results   []DrugResult `json:"results"`
}

// Функция для вычисления скорости введения препарата
func calculateInfusionSpeed(drug DrugData) float64 {
	// Формула: 
	// total_drug_mg = concentration * ampoules_count * ampoule_volume
	// drug_mg_per_hour = (infusion_speed_ml_hour / solvent_volume) * total_drug_mg
	// infusion_speed = drug_mg_per_hour / patient_weight
	
	totalDrugMg := drug.DrugConcentration * float64(drug.AmpoulesCount) * drug.AmpouleVolume
	infusionSpeedMLHour := drug.SolventVolume // Предполагается 1 мл/час
	drugMgPerHour := (infusionSpeedMLHour / drug.SolventVolume) * totalDrugMg
	infusionSpeed := drugMgPerHour / drug.PatientWeight
	
	// Округляем до 2 знаков после запятой
	return float64(int(infusionSpeed*100)) / 100
}

// Функция для отправки POST-запроса с результатами к Django
func sendResultsToDjango(orderID int, results []DrugResult) error {
	url := fmt.Sprintf("%s/api/orders/async/update_results/", DJANGO_SERVICE_URL)
	
	data := ResultsData{
		SecretKey: SECRET_KEY,
		OrderID:   orderID,
		Results:   results,
	}
	
	jsonData, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("ошибка сериализации JSON: %v", err)
	}
	
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("ошибка создания запроса: %v", err)
	}
	
	req.Header.Set("Content-Type", "application/json")
	
	client := &http.Client{
		Timeout: 10 * time.Second,
	}
	
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("ошибка отправки запроса: %v", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("Django вернул статус %d", resp.StatusCode)
	}
	
	fmt.Printf("Результаты отправлены для заявки ID: %d (%d препаратов)\n", orderID, len(results))
	return nil
}

// Горутина для выполнения асинхронного расчета скорости введения препаратов
func performAsyncCalculation(orderID int, drugs []DrugData) {
	fmt.Printf("Начат расчет для заявки ID: %d (%d препаратов)\n", orderID, len(drugs))
	
	// Имитация долгого расчета (5-10 секунд)
	delay := time.Duration(5+rand.Intn(6)) * time.Second
	fmt.Printf("Задержка: %v\n", delay)
	time.Sleep(delay)
	
	// Вычисление скорости введения для каждого препарата
	results := make([]DrugResult, 0, len(drugs))
	for _, drug := range drugs {
		infusionSpeed := calculateInfusionSpeed(drug)
		results = append(results, DrugResult{
			DrugInOrderID: drug.DrugInOrderID,
			InfusionSpeed: infusionSpeed,
		})
		fmt.Printf("Препарат %d: скорость введения = %.2f мг/кг/час\n", drug.DrugInOrderID, infusionSpeed)
	}
	
	// Отправка результатов обратно в Django
	err := sendResultsToDjango(orderID, results)
	if err != nil {
		fmt.Printf("Ошибка отправки результатов: %v\n", err)
		return
	}
}

// Обработчик POST-запроса /drugs_process/ для запуска асинхронного расчета
func drugsProcessHandler(c *gin.Context) {
	var req DrugsProcessRequest
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Неверный формат запроса",
			"details": err.Error(),
		})
		return
	}
	
	// Помещаем задачу в очередь (запускаем в горутине)
	go performAsyncCalculation(req.OrderID, req.Drugs)
	
	// Go-сервис принимает задачу, помещает её в очередь и возвращает ответ 202 Accepted
	c.JSON(http.StatusAccepted, gin.H{
		"status":   "accepted",
		"message":  "Задача помещена в очередь на обработку",
		"order_id": req.OrderID,
		"drugs_count": len(req.Drugs),
	})
}

// Обработчик для проверки здоровья сервиса
func healthHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
		"service": "async-calculation-service",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

func main() {
	// Инициализация генератора случайных чисел
	rand.Seed(time.Now().UnixNano())
	
	// Создание Gin router
	r := gin.Default()
	
	// Маршруты
	r.POST("/drugs_process/", drugsProcessHandler)
	r.GET("/health", healthHandler)
	
	// Запуск сервера
	if err := r.Run(PORT); err != nil {
		fmt.Printf("Ошибка запуска сервера: %v\n", err)
	}
}
