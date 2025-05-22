package Controllers

import (
	"context"
	"time"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	healingv1 "HealingOperator/Api/V1"
)

// HealingReconciler reconciles a Healing object
type HealingReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healings,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healings/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healings/finalizers,verbs=update

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
func (r *HealingReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	log.Info("Reconciliando objeto Healing", "namespace", req.Namespace, "name", req.Name)

	// TODO(user): your logic here

	return ctrl.Result{RequeueAfter: time.Minute}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *HealingReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&healingv1.Healing{}).
		Complete(r)
} 