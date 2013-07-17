print __doc__


# Code source: Gael Varoqueux
# Modified for Documentation merge by Jaques Grobler
# License: BSD

import pylab as pl
from mpl_toolkits.mplot3d import Axes3D
from sklearn import datasets
from sklearn.decomposition import PCA

# import some data to play with
iris = datasets.load_iris()
X = iris.data[:, :2]  # we only take the first two features.
Y = iris.target

x_min, x_max = X[:, 0].min() - .5, X[:, 0].max() + .5
y_min, y_max = X[:, 1].min() - .5, X[:, 1].max() + .5

pl.figure(2, figsize=(8, 6))
pl.clf()

# Plot the training points
pl.scatter(X[:, 0], X[:, 1], c=Y, cmap=pl.cm.rainbow)
pl.xlabel('Sepal length')
pl.ylabel('Sepal width')

pl.xlim(x_min, x_max)
pl.ylim(y_min, y_max)
pl.xticks(())
pl.yticks(())

# To getter a better understanding of interaction of the dimensions
# plot the first three PCA dimensions
fig = pl.figure(1, figsize=(8, 6))
ax = Axes3D(fig, elev=-150, azim=110)
X_reduced = PCA(n_components=3).fit_transform(iris.data)
ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2], c=Y,
           cmap=pl.cm.rainbow)
ax.set_title("First three PCA directions")
ax.set_xlabel("1st eigenvector")
ax.set_xticks(())
ax.set_ylabel("2nd eigenvector")
ax.set_yticks(())
ax.set_zlabel("3rd eigenvector")
ax.set_zticks(())

pl.show()