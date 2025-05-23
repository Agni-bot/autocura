package Controllers

import (
	"context"
	"time"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	rollbackv1 "RollbackOperator/Api/V1"
)

// RollbackReconciler reconciles a Rollback object
type RollbackReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=rollback.autocura.io,resources=rollbacks,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=rollback.autocura.io,resources=rollbacks/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=rollback.autocura.io,resources=rollbacks/finalizers,verbs=update

// Reconcile is part of the main kubernetes reconciliation loop which aims to
// move the current state of the cluster closer to the desired state.
func (r *RollbackReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	log.Info("Reconciliando objeto Rollback", "namespace", req.Namespace, "name", req.Name)

	// TODO(user): your logic here

	return ctrl.Result{RequeueAfter: time.Minute}, nil
}

// SetupWithManager sets up the controller with the Manager.
func (r *RollbackReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&rollbackv1.Rollback{}).
		Complete(r)
} 