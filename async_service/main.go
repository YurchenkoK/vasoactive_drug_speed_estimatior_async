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

const (
	DJANGO_SERVICE_URL = "http://localhost:8005"
	SECRET_KEY         = "a1b2c3d4e5f6g7h8"
	PORT               = ":8081"
)

type DrugData struct {
	DrugInEstimationID int     `json:"druginestimation_id" binding:"required"`
	DrugConcentration  float64 `json:"drug_concentration" binding:"required"`
	AmpouleVolume      float64 `json:"ampoule_volume" binding:"required"`
	AmpoulesCount      int     `json:"ampoules_count" binding:"required"`
	SolventVolume      float64 `json:"solvent_volume" binding:"required"`
	PatientWeight      float64 `json:"patient_weight" binding:"required"`
}

type DrugsProcessRequest struct {
	EstimationRequestID int        `json:"estimation_request_id" binding:"required"`
	Drugs               []DrugData `json:"drugs" binding:"required"`
}

type DrugResult struct {
	DrugInEstimationID int     `json:"druginestimation_id"`
	InfusionSpeed      float64 `json:"infusion_speed"`
}

type ResultsData struct {
	SecretKey           string       `json:"secret_key"`
	EstimationRequestID int          `json:"estimation_request_id"`
	Results             []DrugResult `json:"results"`
}

func calculateInfusionSpeed(drug DrugData) float64 {
	totalDrugMg := drug.DrugConcentration * float64(drug.AmpoulesCount) * drug.AmpouleVolume
	infusionSpeedMLHour := drug.SolventVolume
	drugMgPerHour := (infusionSpeedMLHour / drug.SolventVolume) * totalDrugMg
	infusionSpeed := drugMgPerHour / drug.PatientWeight

	return float64(int(infusionSpeed*100)) / 100
}

func sendResultsToDjango(orderID int, results []DrugResult) error {
	url := fmt.Sprintf("%s/api/estimation_requests/async/update_results/", DJANGO_SERVICE_URL)

	data := ResultsData{
		SecretKey:           SECRET_KEY,
		EstimationRequestID: orderID,
		Results:             results,
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

func performAsyncCalculation(estimationRequestID int, drugs []DrugData) {
	fmt.Printf("Начат расчет для заявки ID: %d (%d препаратов)\n", estimationRequestID, len(drugs))

	delay := time.Duration(5+rand.Intn(6)) * time.Second
	fmt.Printf("Задержка: %v\n", delay)
	time.Sleep(delay)

	results := make([]DrugResult, 0, len(drugs))
	for _, drug := range drugs {
		infusionSpeed := calculateInfusionSpeed(drug)
		results = append(results, DrugResult{
			DrugInEstimationID: drug.DrugInEstimationID,
			InfusionSpeed:      infusionSpeed,
		})
		fmt.Printf("Препарат %d: скорость введения = %.2f мг/кг/час\n", drug.DrugInEstimationID, infusionSpeed)
	}

	err := sendResultsToDjango(estimationRequestID, results)
	if err != nil {
		fmt.Printf("Ошибка отправки результатов: %v\n", err)
		return
	}
}

func drugsProcessHandler(c *gin.Context) {
	var req DrugsProcessRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Неверный формат запроса",
			"details": err.Error(),
		})
		return
	}

	go performAsyncCalculation(req.EstimationRequestID, req.Drugs)

	c.JSON(http.StatusAccepted, gin.H{
		"status":                "accepted",
		"message":               "Задача помещена в очередь на обработку",
		"estimation_request_id": req.EstimationRequestID,
		"drugs_count":           len(req.Drugs),
	})
}

func healthHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"service":   "async-calculation-service",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

func main() {
	rand.Seed(time.Now().UnixNano())

	r := gin.Default()

	r.POST("/drugs_process/", drugsProcessHandler)
	r.GET("/health", healthHandler)

	if err := r.Run(PORT); err != nil {
		fmt.Printf("Ошибка запуска сервера: %v\n", err)
	}
}
