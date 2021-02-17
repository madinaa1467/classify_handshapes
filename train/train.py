import keras
# import strategy as strategy
# import tensorflow as tf
from keras import layers, Model
from keras.utils import plot_model

# from data.load_labels import steps_needed
from efficientnet.keras import EfficientNetB4
import sys
sys.path.append('/home/kenny/PycharmProjects/classify_handshapes')
from data.dataset import loadDatabase
from data.const import IMG_SIZE, NUM_CLASSES_TRAIN, LEARNING_RATE, UNFREEZE_LEARNING_RATE,\
    N_EPOCHS, N_WORKERS, TOP_DROPOUT_RATE, MODEL_NAME, HIST_PATH, PLOT_PATH
from model_func import run_model, save_plot_history, plot_acc, test_model


def build_model(model_name, learning_rate, top_dropout_rate, num_classes) -> Model:

    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    # x = img_augmentation(inputs)
    model = EfficientNetB4(include_top=False, input_tensor=inputs, weights="noisy-student")

    # Freeze the pretrained weights
    model.trainable = False

    # Rebuild top
    x = layers.GlobalAveragePooling2D(name="avg_pool")(model.output)
    x = layers.BatchNormalization()(x)

    x = layers.Dropout(top_dropout_rate, name="top_dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="pred")(x)

    # print('1!!!! AAAAAAAA')
    # model.summary()
    plot_model(model, to_file=PLOT_PATH + ".jpg", show_shapes=True)

    # Compile
    model = keras.Model(inputs, outputs, name="EfficientNet")
    optimizer = keras.optimizers.Adam(lr=learning_rate)
    model.compile(
        optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
    )
    # print('2!!!! AAAAAAAA')
    # model.summary()

    return model


def unfreeze_model(model, learning_rate):
    # We unfreeze the top 20 layers while leaving BatchNorm layers frozen
    for layer in model.layers[-20:]:
        if not isinstance(layer, layers.BatchNormalization):
            layer.trainable = True

    optimizer = keras.optimizers.Adam(lr=learning_rate)
    model.compile(
        optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
    )
    print('3!!!! AAAAAAAA')
    model.summary()
    return model

def run():
    train_generator, validation_generator, test_generator = loadDatabase(False)

    # with strategy.scope():
    model = build_model(MODEL_NAME, LEARNING_RATE, TOP_DROPOUT_RATE, NUM_CLASSES_TRAIN)
    model = unfreeze_model(model, UNFREEZE_LEARNING_RATE)

    eff_net_history = run_model(
        model_name=MODEL_NAME,
        hist_path=HIST_PATH,
        model_function=model,
        n_epochs=N_EPOCHS, n_workers=N_WORKERS,
        train_generator=train_generator,
        validation_generator=validation_generator,
        test_generator=test_generator
    )

def test():
    train_generator, validation_generator, test_generator = loadDatabase(False)
    # TODO change it!!!!!!!
    checkpoint = 'gold/5_eff_net_b4_imagenet_weights_epoch-01_val_loss-16.12_val_acc-0.00.hdf5' #TODO name showld be from const
    test_model(checkpoint,
               # build_model(MODEL_NAME, LEARNING_RATE, TOP_DROPOUT_RATE, NUM_CLASSES_TEST),
               test_generator=test_generator)



if __name__ == '__main__':
    run()
    # test()


